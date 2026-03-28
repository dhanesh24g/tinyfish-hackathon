"use client"

import { useState, useEffect } from "react"
import { Mic, MicOff, Volume2, SkipForward, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"

interface VoiceInterviewProps {
  questions: string[]
  currentIndex: number
  onNextQuestion: () => void
  onComplete: () => void
}

type InterviewState = "speaking" | "listening" | "idle"

export function VoiceInterview({ questions, currentIndex, onNextQuestion, onComplete }: VoiceInterviewProps) {
  const [state, setState] = useState<InterviewState>("speaking")
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)

  const currentQuestion = questions[currentIndex]
  const isLastQuestion = currentIndex === questions.length - 1

  // Simulate AI speaking the question
  useEffect(() => {
    setState("speaking")
    const speakDuration = 3000 + (currentQuestion?.length || 0) * 30
    
    const timer = setTimeout(() => {
      setState("idle")
    }, speakDuration)

    return () => clearTimeout(timer)
  }, [currentIndex, currentQuestion])

  // Recording timer
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isRecording])

  const handleStartRecording = () => {
    setIsRecording(true)
    setRecordingTime(0)
    setState("listening")
  }

  const handleStopRecording = () => {
    setIsRecording(false)
    setState("idle")
  }

  const handleNext = () => {
    setIsRecording(false)
    setRecordingTime(0)
    if (isLastQuestion) {
      onComplete()
    } else {
      onNextQuestion()
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
      <div className="max-w-2xl w-full">
        {/* Progress indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {questions.map((_, index) => (
            <div 
              key={index}
              className={`w-3 h-3 rounded-full transition-all ${
                index < currentIndex 
                  ? "bg-primary" 
                  : index === currentIndex 
                    ? "bg-primary animate-pulse w-4 h-4" 
                    : "bg-secondary"
              }`}
            />
          ))}
        </div>

        {/* Question counter */}
        <div className="text-center mb-4">
          <span className="text-sm text-muted-foreground">
            Question {currentIndex + 1} of {questions.length}
          </span>
        </div>

        {/* Voice Assistant UI */}
        <div className="glass-card rounded-3xl p-8 md:p-12 neon-border mb-8">
          {/* AI Avatar */}
          <div className="flex justify-center mb-8">
            <div className="relative">
              <div className={`w-32 h-32 rounded-full glass flex items-center justify-center transition-all duration-300 ${
                state === "speaking" ? "animate-pulse-glow ring-4 ring-primary/30" : 
                state === "listening" ? "ring-4 ring-destructive/30" : ""
              }`}>
                {state === "speaking" ? (
                  <Volume2 className="w-14 h-14 text-primary animate-pulse" />
                ) : state === "listening" ? (
                  <Mic className="w-14 h-14 text-destructive" />
                ) : (
                  <Mic className="w-14 h-14 text-muted-foreground" />
                )}
              </div>
              
              {/* Voice waveform */}
              {(state === "speaking" || state === "listening") && (
                <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 flex items-end gap-1 h-8">
                  {[...Array(7)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-1 rounded-full animate-wave ${
                        state === "speaking" ? "bg-primary" : "bg-destructive"
                      }`}
                      style={{
                        height: `${12 + Math.random() * 20}px`,
                        animationDelay: `${i * 0.1}s`,
                      }}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Status */}
          <div className="text-center mb-6">
            <p className={`text-sm font-medium ${
              state === "speaking" ? "text-primary" : 
              state === "listening" ? "text-destructive" : 
              "text-muted-foreground"
            }`}>
              {state === "speaking" ? "AI is speaking..." : 
               state === "listening" ? "Listening to your answer..." : 
               "Ready for your answer"}
            </p>
          </div>

          {/* Question */}
          <div className="bg-secondary/50 rounded-xl p-6 mb-8">
            <p className="text-lg md:text-xl text-foreground text-center leading-relaxed">
              &ldquo;{currentQuestion}&rdquo;
            </p>
          </div>

          {/* Recording Timer */}
          {isRecording && (
            <div className="text-center mb-6">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-destructive/20 text-destructive">
                <div className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
                <span className="font-mono text-lg">{formatTime(recordingTime)}</span>
              </div>
            </div>
          )}

          {/* Controls */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {!isRecording ? (
              <Button
                size="lg"
                onClick={handleStartRecording}
                disabled={state === "speaking"}
                className="h-14 px-8 text-lg font-semibold bg-primary hover:bg-primary/90 text-primary-foreground disabled:opacity-50"
              >
                <Mic className="w-5 h-5 mr-2" />
                Start Recording
              </Button>
            ) : (
              <Button
                size="lg"
                variant="destructive"
                onClick={handleStopRecording}
                className="h-14 px-8 text-lg font-semibold"
              >
                <MicOff className="w-5 h-5 mr-2" />
                Stop Recording
              </Button>
            )}

            <Button
              size="lg"
              variant="outline"
              onClick={handleNext}
              className="h-14 px-8 text-lg font-semibold border-primary/50 hover:bg-primary/10 text-foreground"
            >
              {isLastQuestion ? (
                <>
                  <CheckCircle2 className="w-5 h-5 mr-2" />
                  Finish Interview
                </>
              ) : (
                <>
                  <SkipForward className="w-5 h-5 mr-2" />
                  Next Question
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Tips */}
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-muted-foreground text-center">
            <span className="text-primary font-medium">Tip:</span> Take your time to think before answering. 
            Speak clearly and provide specific examples when possible.
          </p>
        </div>
      </div>
    </div>
  )
}
