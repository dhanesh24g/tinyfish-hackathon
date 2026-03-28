"use client"

import { useState, useEffect } from "react"
import { Award, Brain, MessageSquare, Target, TrendingUp, RefreshCw, CheckCircle2, AlertCircle, Lightbulb } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import type { JobInput } from "@/app/page"

interface FeedbackDashboardProps {
  jobInput: JobInput
  onRestart: () => void
}

interface Score {
  label: string
  value: number
  icon: React.ReactNode
  color: string
}

export function FeedbackDashboard({ jobInput, onRestart }: FeedbackDashboardProps) {
  const [animatedScores, setAnimatedScores] = useState<Record<string, number>>({})
  const [overallScore, setOverallScore] = useState(0)

  const scores: Score[] = [
    { label: "Confidence", value: 78, icon: <TrendingUp className="w-5 h-5" />, color: "text-primary" },
    { label: "Communication", value: 85, icon: <MessageSquare className="w-5 h-5" />, color: "text-chart-2" },
    { label: "Technical Depth", value: 72, icon: <Brain className="w-5 h-5" />, color: "text-chart-4" },
    { label: "Role Relevance", value: 81, icon: <Target className="w-5 h-5" />, color: "text-chart-3" },
  ]

  const calculatedOverall = Math.round(scores.reduce((acc, s) => acc + s.value, 0) / scores.length)

  // Animate scores on mount
  useEffect(() => {
    scores.forEach((score, index) => {
      setTimeout(() => {
        let current = 0
        const interval = setInterval(() => {
          current += 2
          if (current >= score.value) {
            current = score.value
            clearInterval(interval)
          }
          setAnimatedScores(prev => ({ ...prev, [score.label]: current }))
        }, 20)
      }, index * 200)
    })

    // Animate overall score
    setTimeout(() => {
      let current = 0
      const interval = setInterval(() => {
        current += 1
        if (current >= calculatedOverall) {
          current = calculatedOverall
          clearInterval(interval)
        }
        setOverallScore(current)
      }, 25)
    }, 800)
  }, [])

  const getScoreColor = (value: number) => {
    if (value >= 80) return "text-primary"
    if (value >= 60) return "text-chart-4"
    return "text-destructive"
  }

  const getScoreLabel = (value: number) => {
    if (value >= 85) return "Excellent"
    if (value >= 75) return "Good"
    if (value >= 60) return "Satisfactory"
    return "Needs Improvement"
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
      <div className="max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/20 border border-primary/30 mb-4">
            <Award className="w-10 h-10 text-primary" />
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
            Interview Performance Analysis
          </h2>
          <p className="text-muted-foreground">
            Mock interview results for <span className="text-primary font-medium">{jobInput.candidateName}</span> based on the submitted role requirements
          </p>
        </div>

        {/* Main Score */}
        <div className="glass-card rounded-2xl p-8 neon-border mb-8">
          <div className="flex flex-col md:flex-row items-center gap-8">
            {/* Circular Progress */}
            <div className="relative w-48 h-48 flex-shrink-0">
              <svg className="w-full h-full -rotate-90">
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="12"
                  className="text-secondary"
                />
                <circle
                  cx="96"
                  cy="96"
                  r="80"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="12"
                  strokeLinecap="round"
                  className="text-primary transition-all duration-1000"
                  strokeDasharray={`${(overallScore / 100) * 502.4} 502.4`}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-5xl font-bold ${getScoreColor(overallScore)}`}>
                  {overallScore}%
                </span>
                <span className="text-sm text-muted-foreground mt-1">Readiness Score</span>
              </div>
            </div>

            {/* Score breakdown */}
            <div className="flex-1 w-full space-y-4">
              {scores.map((score) => (
                <div key={score.label}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={score.color}>{score.icon}</span>
                      <span className="text-sm font-medium text-foreground">{score.label}</span>
                    </div>
                    <span className={`text-sm font-bold ${getScoreColor(animatedScores[score.label] || 0)}`}>
                      {animatedScores[score.label] || 0}%
                    </span>
                  </div>
                  <Progress 
                    value={animatedScores[score.label] || 0} 
                    className="h-2 bg-secondary"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Verdict and Insights */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Verdict */}
          <div className="glass-card rounded-xl p-6 border border-primary/30">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle2 className="w-6 h-6 text-primary" />
              <h3 className="text-lg font-semibold text-foreground">Overall Verdict</h3>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              <span className={`font-semibold ${getScoreColor(calculatedOverall)}`}>{getScoreLabel(calculatedOverall)}.</span>{" "}
              Good preparation overall, but consider improving your system design explanations and providing more specific examples in behavioral questions.
            </p>
          </div>

          {/* Areas to Improve */}
          <div className="glass-card rounded-xl p-6 border border-chart-4/30">
            <div className="flex items-center gap-3 mb-4">
              <AlertCircle className="w-6 h-6 text-chart-4" />
              <h3 className="text-lg font-semibold text-foreground">Areas to Improve</h3>
            </div>
            <ul className="space-y-2 text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="text-chart-4 mt-1">•</span>
                <span>Add more quantifiable achievements to answers</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-chart-4 mt-1">•</span>
                <span>Practice explaining complex technical concepts</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-chart-4 mt-1">•</span>
                <span>Use the STAR method for behavioral questions</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Tips */}
        <div className="glass-card rounded-xl p-6 border border-chart-2/30 mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Lightbulb className="w-6 h-6 text-chart-2" />
            <h3 className="text-lg font-semibold text-foreground">Preparation Tips</h3>
          </div>
          <div className="grid sm:grid-cols-2 gap-4 text-sm text-muted-foreground">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
              <span>Research company values and culture beforehand</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
              <span>Prepare questions to ask the interviewer</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
              <span>Practice whiteboard coding if applicable</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
              <span>Review recent company news and products</span>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <Button 
          size="lg"
          onClick={onRestart}
          className="w-full h-14 text-lg font-semibold bg-primary hover:bg-primary/90 text-primary-foreground transition-all duration-300 hover:scale-[1.02] hover:shadow-lg hover:shadow-primary/25"
        >
          <RefreshCw className="w-5 h-5 mr-2" />
          Start New Interview Practice
        </Button>
      </div>
    </div>
  )
}
