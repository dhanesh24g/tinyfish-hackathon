"use client"

import { useState, useEffect } from "react"
import { Brain, Search, MessageSquare, FileText, Lightbulb, CheckCircle2, Loader2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import type { JobInput } from "@/app/page"

interface AgentThinkingPanelProps {
  jobInput: JobInput
  onComplete: (questions: string[]) => void
}

const STEPS = [
  { 
    id: 1, 
    title: "Parsing job description", 
    icon: FileText,
    logs: ["Extracting responsibilities...", "Identifying skill requirements...", "Detecting hiring expectations and role signals..."]
  },
  { 
    id: 2, 
    title: "Searching dynamic web sources", 
    icon: Search,
    logs: ["Collecting Reddit discussions...", "Scanning blog posts and forum threads...", "Finding interview experiences and hiring signals..."]
  },
  { 
    id: 3, 
    title: "Reviewing candidate-relevant insights", 
    icon: MessageSquare,
    logs: ["Comparing candidate profile with role needs...", "Reviewing role-specific patterns...", "Extracting likely interview themes..."]
  },
  { 
    id: 4, 
    title: "Extracting common interview questions", 
    icon: Lightbulb,
    logs: ["Identifying question patterns...", "Categorizing by difficulty...", "Ranking by frequency..."]
  },
  { 
    id: 5, 
    title: "Preparing mock interview", 
    icon: Brain,
    logs: ["Generating personalized questions...", "Calibrating difficulty level...", "Finalizing interview script..."]
  },
]

export function AgentThinkingPanel({ jobInput, onComplete }: AgentThinkingPanelProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const [logs, setLogs] = useState<string[]>([])
  const [completedSteps, setCompletedSteps] = useState<number[]>([])

  useEffect(() => {
    const stepDuration = 2500
    const logInterval = 700

    const runStep = (stepIndex: number) => {
      if (stepIndex >= STEPS.length) {
        // All steps completed
        setTimeout(() => {
          const generatedQuestions = [
            `Tell me about yourself and why this role is the right next step for you.`,
            `Which project or experience best demonstrates your fit for the job described in this posting?`,
            `If you were selected, how would you approach your first 90 days in this role?`,
          ]
          onComplete(generatedQuestions)
        }, 500)
        return
      }

      setCurrentStep(stepIndex)
      const step = STEPS[stepIndex]
      
      // Add logs one by one
      step.logs.forEach((log, i) => {
        setTimeout(() => {
          setLogs(prev => [...prev, `[Step ${stepIndex + 1}] ${log}`])
        }, logInterval * (i + 1))
      })

      // Mark step as complete and move to next
      setTimeout(() => {
        setCompletedSteps(prev => [...prev, stepIndex])
        setProgress(((stepIndex + 1) / STEPS.length) * 100)
        runStep(stepIndex + 1)
      }, stepDuration)
    }

    // Start the process
    setLogs([
      `> Initializing HiTL career agent for ${jobInput.candidateName || "candidate"}...`,
      `> Loading job description and role requirements...`,
      `> Loading candidate profile and interview preferences...`,
    ])
    setTimeout(() => runStep(0), 800)
  }, [jobInput, onComplete])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
      <div className="max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full glass neon-border mb-4 animate-pulse-glow">
            <Brain className="w-10 h-10 text-primary animate-pulse" />
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
            AI Agent Working
          </h2>
          <p className="text-muted-foreground">
            Analyzing the job description, gathering interview intelligence, and tailoring the session for <span className="text-primary font-medium">{jobInput.candidateName}</span>
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-muted-foreground mb-2">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} className="h-3 bg-secondary" />
        </div>

        {/* Steps */}
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
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                    isCompleted 
                      ? "bg-primary/20 text-primary" 
                      : isActive 
                        ? "bg-primary/10 text-primary animate-pulse" 
                        : "bg-secondary text-muted-foreground"
                  }`}>
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

          {/* Terminal Logs */}
          <div className="glass-card rounded-xl p-4 neon-border h-[400px] md:h-auto">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border/50">
              <div className="w-3 h-3 rounded-full bg-destructive/80" />
              <div className="w-3 h-3 rounded-full bg-warning" />
              <div className="w-3 h-3 rounded-full bg-primary" />
              <span className="ml-2 text-sm text-muted-foreground font-mono">agent.log</span>
            </div>
            <div className="font-mono text-sm space-y-1 overflow-y-auto max-h-[320px] md:max-h-[350px]">
              {logs.map((log, index) => (
                <div 
                  key={index} 
                  className={`${log.startsWith(">") ? "text-primary" : "text-muted-foreground"} animate-fade-in`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <span className="text-primary/60 mr-2">$</span>
                  {log}
                  {index === logs.length - 1 && (
                    <span className="inline-block w-2 h-4 bg-primary ml-1 animate-pulse" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
