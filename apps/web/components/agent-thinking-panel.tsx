"use client"

import { useEffect, useState } from "react"
import { Bot, Brain, CheckCircle2, Globe, Loader2, Search, Sparkles } from "lucide-react"
import type { JobInput } from "@/app/page"
import { Progress } from "@/components/ui/progress"
import {
  extractJobTarget,
  getQuestionBank,
  startInterviewSession,
  streamResearch,
  type InterviewSessionResponse,
  type JobTargetResponse,
  type ResearchRunResponse,
} from "@/lib/api"

interface AgentThinkingPanelProps {
  jobInput: JobInput
  onComplete: (payload: {
    jobTarget: JobTargetResponse
    researchResult: ResearchRunResponse
    interviewSession: InterviewSessionResponse
  }) => void
}

const STEPS = [
  { id: 1, title: "Extracting the job posting", icon: Globe },
  { id: 2, title: "TinyFish browsing dynamic sources", icon: Search },
  { id: 3, title: "Ranking interview signals", icon: Sparkles },
  { id: 4, title: "Preparing the live interview session", icon: Brain },
]

export function AgentThinkingPanel({ jobInput, onComplete }: AgentThinkingPanelProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(6)
  const [logs, setLogs] = useState<string[]>([])
  const [completedSteps, setCompletedSteps] = useState<number[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    const workflowStartedAt = Date.now()

    async function runWorkflow() {
      try {
        setLogs([
          `> Initializing TinyFish interview workflow for ${jobInput.firstName}...`,
          `> Navigating to ${jobInput.jobPostingUrl}`,
        ])

        setCurrentStep(0)
        const jobTarget = await extractJobTarget(jobInput.jobPostingUrl)
        if (!isMounted) return

        setCompletedSteps([0])
        setProgress(24)
        setLogs((prev) => [
          ...prev,
          `> Extracted role: ${jobTarget.role_title || "Unknown role"} at ${jobTarget.company_name || "Unknown company"}`,
        ])

        setCurrentStep(1)
        await streamResearch(jobTarget.id, (payload) => {
          if (!isMounted) return

          if (payload.type === "progress") {
            const index = Number(payload.index || 0)
            const total = Number(payload.total || 1)
            const url = String(payload.url || "")
            const status = String(payload.status || "running")
            setProgress(24 + Math.round((index / Math.max(total, 1)) * 50))
            setLogs((prev) => [...prev, `[TinyFish] ${status.toUpperCase()} ${url}`])
          }

          if (payload.type === "complete") {
            setCompletedSteps([0, 1, 2])
            setCurrentStep(3)
            setProgress(82)
            setLogs((prev) => [
              ...prev,
              `> TinyFish completed web collection from ${payload.source_count || 0} sources`,
              `> Building interview session from ranked signals...`,
            ])
          }
        })

        const questions = await getQuestionBank(jobTarget.id)
        if (!isMounted) return

        const completeResearchResult: ResearchRunResponse = {
          job_target_id: jobTarget.id,
          sources: [],
          questions,
        }

        const interviewSession = await startInterviewSession(jobTarget.id, "voice")
        if (!isMounted) return

        setCompletedSteps([0, 1, 2, 3])
        setProgress(100)
        setLogs((prev) => [
          ...prev,
          `> Interview session ready with ${completeResearchResult.questions.length} ranked prompts`,
          `> Handing off to the live interviewer`,
        ])

        const elapsed = Date.now() - workflowStartedAt
        const minVisibleMs = 4500
        if (elapsed < minVisibleMs) {
          await new Promise((resolve) => window.setTimeout(resolve, minVisibleMs - elapsed))
        }

        onComplete({
          jobTarget,
          researchResult: completeResearchResult,
          interviewSession,
        })
      } catch (err) {
        if (!isMounted) return
        setError(err instanceof Error ? err.message : "TinyFish workflow failed")
      }
    }

    runWorkflow()

    return () => {
      isMounted = false
    }
  }, [jobInput, onComplete])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
      <div className="max-w-5xl w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full glass neon-border mb-4 animate-pulse-glow">
            <Brain className="w-10 h-10 text-primary animate-pulse" />
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-2">TinyFish Is Working</h2>
          <p className="text-muted-foreground">
            TinyFish is browsing the job posting, collecting interview intelligence, and preparing the live session for{" "}
            <span className="text-primary font-medium">{jobInput.firstName}</span>
          </p>
        </div>

        <div className="mb-8">
          <div className="flex justify-between text-sm text-muted-foreground mb-2">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} className="h-3 bg-secondary" />
        </div>

        <div className="grid md:grid-cols-2 gap-4 mb-8">
          <div className="space-y-3">
            {STEPS.map((step, index) => {
              const Icon = step.icon
              const isActive = index === currentStep
              const isCompleted = completedSteps.includes(index)

              return (
                <div
                  key={step.id}
                  className={`flex items-center gap-4 p-4 rounded-xl transition-all duration-300 ${
                    isActive
                      ? "glass-card neon-border"
                      : isCompleted
                        ? "glass-card border border-primary/30"
                        : "glass opacity-50"
                  }`}
                >
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                      isCompleted
                        ? "bg-primary/20 text-primary"
                        : isActive
                          ? "bg-primary/10 text-primary animate-pulse"
                          : "bg-secondary text-muted-foreground"
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : isActive ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className={`font-medium ${isActive || isCompleted ? "text-foreground" : "text-muted-foreground"}`}>
                      Step {step.id}
                    </p>
                    <p className={`text-sm ${isActive ? "text-primary" : "text-muted-foreground"}`}>
                      {step.title}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="glass-card rounded-xl p-4 neon-border h-[420px] md:h-auto">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border/50">
              <div className="w-3 h-3 rounded-full bg-destructive/80" />
              <div className="w-3 h-3 rounded-full bg-warning" />
              <div className="w-3 h-3 rounded-full bg-primary" />
              <span className="ml-2 text-sm text-muted-foreground font-mono">tinyfish.scrape.log</span>
            </div>

            <div className="mb-4 rounded-xl border border-primary/20 bg-primary/5 p-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center">
                  <Bot className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-foreground">TinyFish browser worker</p>
                  <p className="text-xs text-muted-foreground">Interactive scraping for JS-rendered job and research pages</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-primary">
                <Sparkles className="w-4 h-4" />
                <span>Collecting company, role, and interview-source signals from the web</span>
              </div>
            </div>

            <div className="font-mono text-sm space-y-1 overflow-y-auto max-h-[280px] md:max-h-[320px]">
              {logs.map((log, index) => (
                <div
                  key={index}
                  className={`${log.startsWith(">") ? "text-primary" : "text-muted-foreground"} animate-fade-in`}
                >
                  <span className="text-primary/60 mr-2">$</span>
                  {log}
                  {index === logs.length - 1 && !error && (
                    <span className="inline-block w-2 h-4 bg-primary ml-1 animate-pulse" />
                  )}
                </div>
              ))}
              {error && (
                <div className="text-destructive">
                  <span className="text-destructive/70 mr-2">$</span>
                  {error}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
