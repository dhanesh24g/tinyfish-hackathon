"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { CheckCircle2, Loader2, Mic, MicOff, Send, Volume2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import {
  getInterviewFeedback,
  sendInterviewEvent,
  stopInterviewSession,
  type FeedbackReportResponse,
  type InterviewSessionResponse,
  type JobTargetResponse,
  type ResearchRunResponse,
} from "@/lib/api"

interface VoiceInterviewProps {
  firstName: string
  jobTarget: JobTargetResponse
  researchResult: ResearchRunResponse
  initialSession: InterviewSessionResponse
  onComplete: (report: FeedbackReportResponse, session: InterviewSessionResponse) => void
}

type InterviewState = "speaking" | "listening" | "idle" | "submitting"

type SpeechRecognitionAlternativeLike = {
  transcript?: string
}

type SpeechRecognitionResultLike = {
  isFinal?: boolean
  [index: number]: SpeechRecognitionAlternativeLike
}

type SpeechRecognitionEventLike = {
  results: ArrayLike<SpeechRecognitionResultLike>
}

type SpeechRecognitionErrorEventLike = {
  error?: string
}

type SpeechRecognitionInstance = EventTarget & {
  continuous: boolean
  interimResults: boolean
  lang: string
  onresult: ((event: SpeechRecognitionEventLike) => void) | null
  onerror: ((event: SpeechRecognitionErrorEventLike) => void) | null
  onend: (() => void) | null
  start(): void
  stop(): void
}

type SpeechRecognitionCtor = new () => SpeechRecognitionInstance

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionCtor
    webkitSpeechRecognition?: SpeechRecognitionCtor
  }
}

function getActivePrompt(session: InterviewSessionResponse): string {
  const reversed = [...session.turns].reverse()
  const nextPrompt = reversed.find(
    (turn) =>
      turn.user_response === null &&
      (turn.event_type === "agent_question" ||
        turn.event_type === "system_prompt" ||
        turn.event_type === "clarification_request"),
  )
  return nextPrompt?.agent_prompt || "Tell me about yourself."
}

export function VoiceInterview({
  firstName,
  jobTarget,
  researchResult,
  initialSession,
  onComplete,
}: VoiceInterviewProps) {
  const [session, setSession] = useState(initialSession)
  const [state, setState] = useState<InterviewState>("speaking")
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [transcript, setTranscript] = useState("")
  const [interimTranscript, setInterimTranscript] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [speechSupported, setSpeechSupported] = useState(false)
  const [micPermissionGranted, setMicPermissionGranted] = useState(false)
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null)
  const lastQuestionRef = useRef<string>("")

  const currentQuestion = useMemo(() => getActivePrompt(session), [session])
  const totalQuestions = Math.max(researchResult.questions.length, 1)
  const answeredQuestions = session.turns.filter((turn) => turn.user_response).length
  const progressCount = Math.min(answeredQuestions + 1, totalQuestions)

  useEffect(() => {
    const requestMicPermission = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        stream.getTracks().forEach(track => track.stop())
        setMicPermissionGranted(true)
      } catch (err) {
        console.error("Microphone permission denied:", err)
        setError("Microphone permission is required for voice answers. Please enable it in your browser settings.")
      }
    }

    const SpeechRecognitionImpl = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognitionImpl) {
      setSpeechSupported(true)

      if (typeof navigator !== 'undefined' && navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
        requestMicPermission()
      } else {
        setMicPermissionGranted(true)
      }

      const recognition = new SpeechRecognitionImpl()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = "en-US"

      recognition.onresult = (event) => {
        let finalText = ""
        let interimText = ""

        for (let i = 0; i < event.results.length; i += 1) {
          const result = event.results[i]
          const text = result[0]?.transcript ?? ""
          if (result.isFinal) {
            finalText += text
          } else {
            interimText += text
          }
        }

        if (finalText) {
          const lowerText = finalText.toLowerCase()
          if (lowerText.includes("repeat") || lowerText.includes("repeat the question") || lowerText.includes("say that again") || lowerText.includes("what was the question")) {
            handleRepeatQuestion()
            return
          }
          setTranscript((prev) => `${prev} ${finalText}`.trim())
        }
        setInterimTranscript(interimText.trim())
      }

      recognition.onerror = (event) => {
        setError(`Speech recognition error: ${event.error}`)
        setIsRecording(false)
        setState("idle")
      }

      recognition.onend = () => {
        setIsRecording(false)
        setInterimTranscript("")
        setState((prev) => (prev === "submitting" ? prev : "idle"))
      }

      recognitionRef.current = recognition
    }

    return () => {
      window.speechSynthesis?.cancel()
      recognitionRef.current?.stop()
    }
  }, [])

  useEffect(() => {
    if (currentQuestion === lastQuestionRef.current) {
      return
    }

    lastQuestionRef.current = currentQuestion
    setTranscript("")
    setInterimTranscript("")
    setError(null)
    setState((prev) => (prev === "submitting" ? prev : "speaking"))

    const utterance = new SpeechSynthesisUtterance(currentQuestion)
    utterance.rate = 0.98
    utterance.pitch = 1
    utterance.onend = () => setState((prev) => (prev === "submitting" ? prev : "idle"))

    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel()
      window.speechSynthesis.speak(utterance)
    } else {
      const timer = globalThis.setTimeout(() => setState((prev) => (prev === "submitting" ? prev : "idle")), 1800)
      return () => globalThis.clearTimeout(timer)
    }

    return () => {
      window.speechSynthesis.cancel()
    }
  }, [currentQuestion])

  useEffect(() => {
    let interval: NodeJS.Timeout | undefined
    if (isRecording) {
      interval = setInterval(() => setRecordingTime((prev) => prev + 1), 1000)
    }
    return () => interval && clearInterval(interval)
  }, [isRecording])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  const handleStartRecording = () => {
    setError(null)
    setRecordingTime(0)
    setIsRecording(true)
    setState("listening")
    recognitionRef.current?.start()
  }

  const handleStopRecording = () => {
    recognitionRef.current?.stop()
    setIsRecording(false)
    setState("idle")
  }

  const handleRepeatQuestion = () => {
    window.speechSynthesis?.cancel()
    recognitionRef.current?.stop()
    setIsRecording(false)
    setState("speaking")

    const utterance = new SpeechSynthesisUtterance(currentQuestion)
    utterance.rate = 0.98
    utterance.pitch = 1
    utterance.onend = () => setState("idle")

    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.speak(utterance)
    } else {
      setState("idle")
    }
  }

  const handleSubmitAnswer = async () => {
    const answer = `${transcript} ${interimTranscript}`.trim()
    if (!answer) {
      setError("Speak or type an answer before submitting.")
      return
    }

    setState("submitting")
    setError(null)
    window.speechSynthesis?.cancel()
    recognitionRef.current?.stop()
    setIsRecording(false)

    try {
      const updatedSession = await sendInterviewEvent(session.id, {
        event_type: "user_text",
        payload: answer,
      })

      setSession(updatedSession)
      setTranscript("")
      setInterimTranscript("")
      setRecordingTime(0)

      if (updatedSession.status === "completed") {
        const report = await getInterviewFeedback(updatedSession.id)
        onComplete(report, updatedSession)
        return
      }

      setState("speaking")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to submit answer")
      setState("idle")
    }
  }

  const handleEndInterview = async () => {
    // Confirmation dialog
    const confirmed = window.confirm(
      "Are you sure you want to end the interview?\n\n" +
      "This will generate your final feedback report based on your answers so far."
    )

    if (!confirmed) {
      return
    }

    setState("submitting")
    setError(null)
    window.speechSynthesis?.cancel()
    recognitionRef.current?.stop()
    setIsRecording(false)

    try {
      const stoppedSession = await stopInterviewSession(session.id)
      const report = await getInterviewFeedback(stoppedSession.id)
      onComplete(report, stoppedSession)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to end interview")
      setState("idle")
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
      <div className="max-w-3xl w-full">
        <div className="flex items-center justify-center gap-2 mb-8">
          {Array.from({ length: totalQuestions }).map((_, index) => (
            <div
              key={index}
              className={`w-3 h-3 rounded-full transition-all ${index + 1 < progressCount
                ? "bg-primary"
                : index + 1 === progressCount
                  ? "bg-primary animate-pulse w-4 h-4"
                  : "bg-secondary"
                }`}
            />
          ))}
        </div>

        <div className="text-center mb-4">
          <span className="text-sm text-muted-foreground">
            {jobTarget.role_title || "Interview"} at {jobTarget.company_name || "target company"}
          </span>
        </div>

        <div className="glass-card rounded-3xl p-6 md:p-12 neon-border mb-6 md:mb-8">
          <div className="flex justify-center mb-6 md:mb-8">
            <div className="relative">
              <button
                onClick={handleRepeatQuestion}
                disabled={state === "submitting"}
                className={`w-28 h-28 md:w-32 md:h-32 rounded-full glass flex items-center justify-center transition-all duration-300 cursor-pointer hover:scale-105 disabled:cursor-not-allowed disabled:hover:scale-100 ${state === "speaking"
                  ? "animate-pulse-glow ring-4 ring-primary/30"
                  : state === "listening"
                    ? "ring-4 ring-destructive/30"
                    : ""
                  }`}
                title="Click to repeat the question"
              >
                {state === "speaking" ? (
                  <Volume2 className="w-12 h-12 md:w-14 md:h-14 text-primary animate-pulse" />
                ) : state === "listening" ? (
                  <Mic className="w-12 h-12 md:w-14 md:h-14 text-destructive" />
                ) : state === "submitting" ? (
                  <Loader2 className="w-12 h-12 md:w-14 md:h-14 text-primary animate-spin" />
                ) : (
                  <Mic className="w-12 h-12 md:w-14 md:h-14 text-muted-foreground" />
                )}
              </button>
            </div>
          </div>

          <div className="text-center mb-6">
            <p
              className={`text-sm font-medium ${state === "speaking"
                ? "text-primary"
                : state === "listening"
                  ? "text-destructive"
                  : "text-muted-foreground"
                }`}
            >
              {state === "speaking"
                ? `AI interviewer is speaking to ${firstName}...`
                : state === "listening"
                  ? "Listening for your answer..."
                  : state === "submitting"
                    ? "Generating your feedback report..."
                    : "Ready when you are"}
            </p>
          </div>

          <div className="bg-secondary/50 rounded-xl p-5 md:p-6 mb-5 md:mb-6">
            <p className="text-base md:text-xl text-foreground text-center leading-relaxed">
              &ldquo;{currentQuestion}&rdquo;
            </p>
          </div>

          {isRecording && (
            <div className="text-center mb-6">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-destructive/20 text-destructive">
                <div className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
                <span className="font-mono text-lg">{formatTime(recordingTime)}</span>
              </div>
            </div>
          )}

          <div className="space-y-4 mb-6">
            <div className="rounded-xl border border-border/40 bg-secondary/30 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground mb-2">Live Transcript</p>
              <p className="text-sm text-foreground min-h-8">
                {`${transcript} ${interimTranscript}`.trim() || "Your spoken answer will appear here. You can edit it before submitting."}
              </p>
            </div>

            <Textarea
              value={transcript}
              onChange={(event) => setTranscript(event.target.value)}
              placeholder="Type your answer here if you prefer text input or want to edit the speech transcript before sending."
              className="min-h-[120px] md:min-h-[120px] text-base bg-secondary/50 border-border/50 focus:border-primary"
            />
          </div>

          {error && <p className="text-sm text-destructive mb-4 text-center">{error}</p>}

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {!isRecording ? (
              <Button
                size="lg"
                onClick={handleStartRecording}
                disabled={!speechSupported || !micPermissionGranted || state === "speaking" || state === "submitting"}
                className="min-h-[48px] px-8 text-base font-semibold bg-primary hover:bg-primary/90 text-primary-foreground disabled:opacity-50"
              >
                <Mic className="w-5 h-5 mr-2" />
                {!speechSupported ? "Speech Not Supported" : !micPermissionGranted ? "Microphone Permission Required" : "Start Voice Answer"}
              </Button>
            ) : (
              <Button
                size="lg"
                variant="destructive"
                onClick={handleStopRecording}
                className="min-h-[48px] px-8 text-base font-semibold"
              >
                <MicOff className="w-5 h-5 mr-2" />
                Stop Recording
              </Button>
            )}

            <Button
              size="lg"
              onClick={handleSubmitAnswer}
              disabled={state === "speaking" || state === "submitting"}
              className="min-h-[48px] px-8 text-base font-semibold bg-primary/90 hover:bg-primary text-primary-foreground"
            >
              <Send className="w-5 h-5 mr-2" />
              Submit Answer
            </Button>
          </div>
        </div>

        <div className="glass rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground text-center sm:text-left">
            Voice mode uses browser text-to-speech for the AI and browser speech-to-text for your answer. Click the speaker icon or say &quot;repeat&quot; to hear the question again. You can always edit or type before sending.
          </p>
          <Button variant="outline" onClick={handleEndInterview} disabled={state === "submitting"}>
            {state === "submitting" ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4 mr-2" />
                End Interview
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
