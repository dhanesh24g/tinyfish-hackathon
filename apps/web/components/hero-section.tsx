"use client"

import { useState } from "react"
import { Brain, FileText, Mic, Search, Sparkles, UserRound } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import type { JobInput } from "@/app/page"

interface HeroSectionProps {
  onStartResearch: (input: JobInput) => void
}

export function HeroSection({ onStartResearch }: HeroSectionProps) {
  const [jobDescription, setJobDescription] = useState("")
  const [candidateName, setCandidateName] = useState("")
  const [candidateEmail, setCandidateEmail] = useState("")
  const [candidatePhone, setCandidatePhone] = useState("")
  const [candidateUniversity, setCandidateUniversity] = useState("")
  const [candidateExperience, setCandidateExperience] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (jobDescription && candidateName && candidateEmail) {
      onStartResearch({
        jobDescription,
        candidateName,
        candidateEmail,
        candidatePhone,
        candidateUniversity,
        candidateExperience,
      })
    }
  }

  return (
    <div className="h-screen flex items-center justify-center px-4 py-4 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-primary/10 blur-3xl animate-float" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-accent/10 blur-3xl animate-float" style={{ animationDelay: "1s" }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[620px] h-[620px] rounded-full border border-primary/10 animate-spin-slow" />
      </div>

      <div className="relative z-10 w-full max-w-[70rem] scale-[0.93] origin-center">
        <div className="flex items-center justify-center gap-4 mb-4">
          <div className="relative">
            <div className="w-14 h-14 md:w-16 md:h-16 rounded-full glass neon-border flex items-center justify-center animate-pulse-glow">
              <Brain className="w-8 h-8 md:w-9 md:h-9 text-primary" />
            </div>
            <Sparkles className="absolute -top-1 -right-1 w-4 h-4 text-primary animate-pulse" />
          </div>
          <div className="text-center">
            <h1 className="text-3xl md:text-[2.7rem] font-bold leading-tight">
              <span className="neon-text text-primary">AI Career</span>{" "}
              <span className="text-foreground">Interview Agent</span>
            </h1>
            <p className="text-base md:text-lg text-muted-foreground max-w-3xl">
              Configure a professional interview preparation session using the job description and the candidate profile.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap justify-center gap-2.5 mb-4">
          <FeatureBadge icon={<Search className="w-4 h-4" />} text="Role Intelligence" />
          <FeatureBadge icon={<Mic className="w-4 h-4" />} text="Voice Interview" />
          <FeatureBadge icon={<Brain className="w-4 h-4" />} text="Adaptive Feedback" />
        </div>

        <form onSubmit={handleSubmit} className="glass-card rounded-[1.5rem] p-4 md:p-5 neon-border shadow-2xl">
          <div className="grid xl:grid-cols-[1.05fr_0.95fr] gap-4">
            <section className="space-y-3">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.22em] text-primary/80 mb-1.5">
                  Interview Setup
                </p>
                <h2 className="text-2xl md:text-[2rem] font-semibold text-foreground">
                  Job Description
                </h2>
                <p className="text-base text-muted-foreground mt-1.5">
                  Paste the complete role details so the agent can prepare relevant questions and assess fit accurately.
                </p>
              </div>

              <div className="glass rounded-2xl border border-primary/15 p-3.5">
                <div className="flex items-center gap-3 mb-2.5">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-foreground">Job Description</p>
                    <p className="text-xs text-muted-foreground">Required</p>
                  </div>
                </div>
                <label htmlFor="jobDescription" className="sr-only">
                  Job Description
                </label>
                <Textarea
                  id="jobDescription"
                  placeholder="Paste the role summary, responsibilities, technical requirements, qualifications, and any hiring expectations..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="bg-secondary/50 border-border/50 focus:border-primary min-h-[210px] resize-none text-base text-foreground placeholder:text-muted-foreground"
                  required
                />
              </div>
            </section>

            <section className="space-y-3">
              <div>
                <h2 className="text-2xl md:text-[2rem] font-semibold text-foreground">
                  Candidate Profile
                </h2>
                <p className="text-base text-muted-foreground mt-1.5">
                  Add the candidate details needed to personalize the live interview and final evaluation.
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-3">
                <FormField label="Full Name" required htmlFor="candidateName">
                  <Input
                    id="candidateName"
                    placeholder="Enter full name"
                    value={candidateName}
                    onChange={(e) => setCandidateName(e.target.value)}
                    className="bg-secondary/50 border-border/50 focus:border-primary h-11 text-base text-foreground placeholder:text-muted-foreground"
                    required
                  />
                </FormField>

                <FormField label="Email Address" required htmlFor="candidateEmail">
                  <Input
                    id="candidateEmail"
                    type="email"
                    placeholder="Enter email address"
                    value={candidateEmail}
                    onChange={(e) => setCandidateEmail(e.target.value)}
                    className="bg-secondary/50 border-border/50 focus:border-primary h-11 text-base text-foreground placeholder:text-muted-foreground"
                    required
                  />
                </FormField>
              </div>

              <div className="grid md:grid-cols-2 gap-3">
                <FormField label="Contact Number" htmlFor="candidatePhone">
                  <Input
                    id="candidatePhone"
                    placeholder="Enter phone number"
                    value={candidatePhone}
                    onChange={(e) => setCandidatePhone(e.target.value)}
                    className="bg-secondary/50 border-border/50 focus:border-primary h-11 text-base text-foreground placeholder:text-muted-foreground"
                  />
                </FormField>

                <FormField label="Experience Level" htmlFor="candidateExperience">
                  <Input
                    id="candidateExperience"
                    placeholder="e.g. Final-year student / 2 years experience"
                    value={candidateExperience}
                    onChange={(e) => setCandidateExperience(e.target.value)}
                    className="bg-secondary/50 border-border/50 focus:border-primary h-11 text-base text-foreground placeholder:text-muted-foreground"
                  />
                </FormField>
              </div>

              <FormField label="Education / Current Organization" htmlFor="candidateUniversity">
                <Input
                  id="candidateUniversity"
                  placeholder="e.g. NUS Computer Science / Software Engineer at ABC"
                  value={candidateUniversity}
                  onChange={(e) => setCandidateUniversity(e.target.value)}
                  className="bg-secondary/50 border-border/50 focus:border-primary h-11 text-base text-foreground placeholder:text-muted-foreground"
                />
              </FormField>
            </section>
          </div>

          <div className="mt-4 pt-4 border-t border-border/40 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <div className="flex items-start gap-3 max-w-2xl">
              <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center flex-shrink-0">
                <UserRound className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">Professional interview intake</p>
                <p className="text-sm text-muted-foreground">
                  After submission, the agent can analyze the job description, tailor the interview plan, and prepare the voice session.
                </p>
              </div>
            </div>

            <Button
              type="submit"
              size="lg"
              className="w-full md:w-auto md:min-w-[260px] h-11 md:h-12 text-base font-semibold bg-primary hover:bg-primary/90 text-primary-foreground transition-all duration-300 hover:scale-[1.02] hover:shadow-lg hover:shadow-primary/25"
              disabled={!jobDescription || !candidateName || !candidateEmail}
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Begin Interview Preparation
            </Button>
          </div>
        </form>

        <p className="text-center text-sm text-muted-foreground mt-4">
          Powered by agent orchestration, voice AI, and interview intelligence
        </p>
      </div>
    </div>
  )
}

function FeatureBadge({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 rounded-full glass border border-primary/20">
      <span className="text-primary">{icon}</span>
      <span className="text-sm font-medium text-foreground">{text}</span>
    </div>
  )
}

function FormField({
  label,
  htmlFor,
  required = false,
  children,
}: {
  label: string
  htmlFor: string
  required?: boolean
  children: React.ReactNode
}) {
  return (
    <div>
      <label htmlFor={htmlFor} className="block text-sm font-medium text-muted-foreground mb-1.5">
        {label}
        {required ? " *" : ""}
      </label>
      {children}
    </div>
  )
}
