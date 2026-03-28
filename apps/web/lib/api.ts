export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000"

export interface JobTargetResponse {
  id: number
  job_posting_url: string
  company_name: string | null
  role_title: string | null
  job_description: string | null
  extraction_confidence: number | null
  status: string
}

export interface QuestionResponse {
  id: number
  text: string
  final_score: number
  category: string | null
}

export interface ResearchRunResponse {
  job_target_id: number
  sources: Array<{ id: number; source_url: string; source_type: string }>
  questions: QuestionResponse[]
}

export interface InterviewTurnResponse {
  id: number
  question_id: number | null
  turn_index: number
  agent_prompt: string
  user_response: string | null
  event_type: string
  created_at: string
}

export interface InterviewSessionResponse {
  id: number
  job_target_id: number
  status: string
  mode: string
  current_question_index: number
  stop_reason: string | null
  started_at: string
  ended_at: string | null
  turns: InterviewTurnResponse[]
}

export interface FeedbackReportResponse {
  id: number
  session_id: number
  summary: string
  overall_score: number
  strengths: string[]
  improvement_areas: string[]
  prep_guidance: string[]
  created_at: string
}

async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(errorText || `API request failed: ${response.status}`)
  }

  return response.json() as Promise<T>
}

export function extractJobTarget(jobPostingUrl: string) {
  return apiRequest<JobTargetResponse>("/job-targets/extract", {
    method: "POST",
    body: JSON.stringify({ job_posting_url: jobPostingUrl }),
  })
}

export function runResearch(jobTargetId: number) {
  return apiRequest<ResearchRunResponse>("/research/run", {
    method: "POST",
    body: JSON.stringify({ job_target_id: jobTargetId, stream: false }),
  })
}

export async function streamResearch(
  jobTargetId: number,
  onMessage: (payload: Record<string, unknown>) => void,
) {
  const response = await fetch(`${API_BASE_URL}/research/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_target_id: jobTargetId, stream: true }),
  })

  if (!response.ok || !response.body) {
    throw new Error("Unable to start TinyFish research stream")
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const chunks = buffer.split("\n\n")
    buffer = chunks.pop() || ""

    for (const chunk of chunks) {
      const dataLine = chunk.split("\n").find((line) => line.startsWith("data: "))
      if (!dataLine) continue
      const payload = JSON.parse(dataLine.slice(6))
      onMessage(payload)
    }
  }
}

export function getQuestionBank(jobTargetId: number) {
  return apiRequest<QuestionResponse[]>(`/question-bank/${jobTargetId}`)
}

export function startInterviewSession(jobTargetId: number, mode: "text" | "voice") {
  return apiRequest<InterviewSessionResponse>("/interview/session/start", {
    method: "POST",
    body: JSON.stringify({ job_target_id: jobTargetId, mode }),
  })
}

export function sendInterviewEvent(
  sessionId: number,
  payload: {
    event_type: "user_text" | "user_audio_chunk" | "clarification_request" | "stop_interview"
    payload: string | null
  },
) {
  return apiRequest<InterviewSessionResponse>(`/interview/session/${sessionId}/event`, {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export function stopInterviewSession(sessionId: number) {
  return apiRequest<InterviewSessionResponse>(`/interview/session/${sessionId}/stop`, {
    method: "POST",
  })
}

export function getInterviewFeedback(sessionId: number) {
  return apiRequest<FeedbackReportResponse>(`/interview/session/${sessionId}/feedback`)
}
