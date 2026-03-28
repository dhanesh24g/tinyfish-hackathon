"use client"

import { useCallback, useState } from "react"
import { AgentThinkingPanel } from "@/components/agent-thinking-panel"
import { FeedbackDashboard } from "@/components/feedback-dashboard"
import { HeroSection } from "@/components/hero-section"
import { VoiceInterview } from "@/components/voice-interview"
import type {
  FeedbackReportResponse,
  InterviewSessionResponse,
  JobTargetResponse,
  ResearchRunResponse,
} from "@/lib/api"

export type AppState = "hero" | "thinking" | "interview" | "feedback"

export interface JobInput {
  jobPostingUrl: string
  firstName: string
  email?: string
  currentFocus?: string
}

export default function Home() {
  const [appState, setAppState] = useState<AppState>("hero")
  const [jobInput, setJobInput] = useState<JobInput>({
    jobPostingUrl: "",
    firstName: "",
    email: "",
    currentFocus: "",
  })
  const [jobTarget, setJobTarget] = useState<JobTargetResponse | null>(null)
  const [researchResult, setResearchResult] = useState<ResearchRunResponse | null>(null)
  const [interviewSession, setInterviewSession] = useState<InterviewSessionResponse | null>(null)
  const [feedback, setFeedback] = useState<FeedbackReportResponse | null>(null)

  const handleStartResearch = useCallback((input: JobInput) => {
    setJobInput(input)
    setAppState("thinking")
  }, [])

  const handleResearchComplete = useCallback((payload: {
    jobTarget: JobTargetResponse
    researchResult: ResearchRunResponse
    interviewSession: InterviewSessionResponse
  }) => {
    setJobTarget(payload.jobTarget)
    setResearchResult(payload.researchResult)
    setInterviewSession(payload.interviewSession)
    setAppState("interview")
  }, [])

  const handleInterviewComplete = useCallback((report: FeedbackReportResponse, session: InterviewSessionResponse) => {
    setFeedback(report)
    setInterviewSession(session)
    setAppState("feedback")
  }, [])

  const handleRestart = useCallback(() => {
    setAppState("hero")
    setJobInput({
      jobPostingUrl: "",
      firstName: "",
      email: "",
      currentFocus: "",
    })
    setJobTarget(null)
    setResearchResult(null)
    setInterviewSession(null)
    setFeedback(null)
  }, [])

  return (
    <main className="min-h-screen gradient-bg">
      {appState === "hero" && <HeroSection onStartResearch={handleStartResearch} />}

      {appState === "thinking" && (
        <AgentThinkingPanel
          jobInput={jobInput}
          onComplete={handleResearchComplete}
          onBack={handleRestart}
        />
      )}

      {appState === "interview" && interviewSession && jobTarget && researchResult && (
        <VoiceInterview
          firstName={jobInput.firstName}
          jobTarget={jobTarget}
          researchResult={researchResult}
          initialSession={interviewSession}
          onComplete={handleInterviewComplete}
        />
      )}

      {appState === "feedback" && feedback && (
        <FeedbackDashboard jobInput={jobInput} feedback={feedback} onRestart={handleRestart} />
      )}
    </main>
  )
}
