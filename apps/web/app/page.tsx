"use client"

import { useState } from "react"
import { HeroSection } from "@/components/hero-section"
import { AgentThinkingPanel } from "@/components/agent-thinking-panel"
import { InterviewQuestions } from "@/components/interview-questions"
import { VoiceInterview } from "@/components/voice-interview"
import { FeedbackDashboard } from "@/components/feedback-dashboard"

export type AppState = "hero" | "thinking" | "questions" | "interview" | "feedback"

export interface JobInput {
  jobDescription: string
  candidateName: string
  candidateEmail: string
  candidatePhone: string
  candidateUniversity: string
  candidateExperience: string
}

export default function Home() {
  const [appState, setAppState] = useState<AppState>("hero")
  const [jobInput, setJobInput] = useState<JobInput>({
    jobDescription: "",
    candidateName: "",
    candidateEmail: "",
    candidatePhone: "",
    candidateUniversity: "",
    candidateExperience: "",
  })
  const [questions, setQuestions] = useState<string[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)

  const handleStartResearch = (input: JobInput) => {
    setJobInput(input)
    setAppState("thinking")
  }

  const handleResearchComplete = (generatedQuestions: string[]) => {
    setQuestions(generatedQuestions)
    setAppState("questions")
  }

  const handleStartInterview = () => {
    setCurrentQuestionIndex(0)
    setAppState("interview")
  }

  const handleInterviewComplete = () => {
    setAppState("feedback")
  }

  const handleRestart = () => {
    setAppState("hero")
    setJobInput({
      jobDescription: "",
      candidateName: "",
      candidateEmail: "",
      candidatePhone: "",
      candidateUniversity: "",
      candidateExperience: "",
    })
    setQuestions([])
    setCurrentQuestionIndex(0)
  }

  return (
    <main className="min-h-screen gradient-bg">
      {appState === "hero" && (
        <HeroSection onStartResearch={handleStartResearch} />
      )}
      
      {appState === "thinking" && (
        <AgentThinkingPanel 
          jobInput={jobInput} 
          onComplete={handleResearchComplete} 
        />
      )}
      
      {appState === "questions" && (
        <InterviewQuestions 
          questions={questions} 
          jobInput={jobInput}
          onStartInterview={handleStartInterview} 
        />
      )}
      
      {appState === "interview" && (
        <VoiceInterview 
          questions={questions}
          currentIndex={currentQuestionIndex}
          onNextQuestion={() => setCurrentQuestionIndex(prev => prev + 1)}
          onComplete={handleInterviewComplete}
        />
      )}
      
      {appState === "feedback" && (
        <FeedbackDashboard 
          jobInput={jobInput}
          onRestart={handleRestart} 
        />
      )}
    </main>
  )
}
