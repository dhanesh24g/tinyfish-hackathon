"use client"

import { CheckCircle2, Mic, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { JobInput } from "@/app/page"

interface InterviewQuestionsProps {
  questions: string[]
  jobInput: JobInput
  onStartInterview: () => void
}

export function InterviewQuestions({ questions, jobInput, onStartInterview }: InterviewQuestionsProps) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
      <div className="max-w-3xl w-full">
        {/* Success Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/20 border border-primary/30 mb-4">
            <CheckCircle2 className="w-10 h-10 text-primary" />
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
            Research Complete!
          </h2>
          <p className="text-muted-foreground">
            AI generated interview questions tailored for <span className="text-primary font-medium">{jobInput.candidateName}</span> based on the submitted job description
          </p>
        </div>

        {/* Questions Card */}
        <div className="glass-card rounded-2xl p-6 md:p-8 neon-border mb-8">
          <div className="flex items-center gap-3 mb-6 pb-4 border-b border-border/50">
            <Sparkles className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-foreground">
              AI Generated Interview Questions
            </h3>
          </div>

          <div className="space-y-4">
            {questions.map((question, index) => (
              <div 
                key={index}
                className="flex gap-4 p-4 rounded-xl bg-secondary/30 border border-border/30 transition-all hover:border-primary/30"
              >
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                  <span className="text-sm font-bold text-primary">{index + 1}</span>
                </div>
                <p className="text-foreground leading-relaxed pt-1">
                  {question}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <StatCard label="Questions" value={questions.length.toString()} />
          <StatCard label="Sources Analyzed" value="47" />
          <StatCard label="Accuracy" value="94%" />
        </div>

        {/* Start Interview Button */}
        <Button 
          size="lg"
          onClick={onStartInterview}
          className="w-full h-14 text-lg font-semibold bg-primary hover:bg-primary/90 text-primary-foreground transition-all duration-300 hover:scale-[1.02] hover:shadow-lg hover:shadow-primary/25"
        >
          <Mic className="w-5 h-5 mr-2" />
          Start Voice Interview
        </Button>

        <p className="text-center text-sm text-muted-foreground mt-4">
          The AI will ask you each question and listen to your response
        </p>
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="glass-card rounded-xl p-4 text-center border border-border/30">
      <p className="text-2xl font-bold text-primary mb-1">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  )
}
