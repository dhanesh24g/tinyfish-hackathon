from __future__ import annotations

import json
from typing import Any

from langchain_core.prompts import PromptTemplate
from openai import OpenAI

from app.core.config import get_settings


class LLMProvider:
    def extract_job_metadata(self, raw_text: str, url: str) -> dict[str, Any]:
        raise NotImplementedError

    def extract_questions(
        self,
        context: str,
        company_name: str = "",
        role_title: str = "",
        job_description: str = "",
    ) -> list[dict[str, Any]]:
        raise NotImplementedError

    def infer_questions_from_jd(self, company_name: str, role_title: str, job_description: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    def generate_answer_guide(self, question: str, job_description: str) -> str:
        raise NotImplementedError

    def evaluate_answer(self, question: str, answer: str, job_description: str) -> dict[str, Any]:
        raise NotImplementedError

    def answer_clarification(self, question: str) -> str:
        raise NotImplementedError

    def generate_feedback(self, transcript: str, evaluations: list[dict[str, Any]]) -> dict[str, Any]:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    def extract_job_metadata(self, raw_text: str, url: str) -> dict[str, Any]:
        return {
            "company_name": "TinyFish Labs",
            "role_title": "Senior Backend Engineer",
            "job_description": raw_text[:1200],
            "confidence": 0.89,
        }

    def extract_questions(
        self,
        context: str,
        company_name: str = "",
        role_title: str = "",
        job_description: str = "",
    ) -> list[dict[str, Any]]:
        return [
            {
                "text": f"Walk me through a recent project that maps to the {role_title or 'target role'} responsibilities.",
                "category": "behavioral",
                "importance": 0.95,
            },
            {"text": "How would you design a scalable FastAPI backend?", "category": "technical", "importance": 0.92},
            {"text": "Describe a time you improved reliability in production.", "category": "behavioral", "importance": 0.83},
        ]

    def infer_questions_from_jd(self, company_name: str, role_title: str, job_description: str) -> list[dict[str, Any]]:
        return [
            {"text": f"Why are you interested in {company_name}?", "category": "company_fit", "importance": 0.8},
            {"text": f"How do you approach the core responsibilities of a {role_title}?", "category": "role_fit", "importance": 0.85},
        ]

    def generate_answer_guide(self, question: str, job_description: str) -> str:
        return f"Use STAR, tie the answer back to the role, and explicitly reference impact for: {question}"

    def evaluate_answer(self, question: str, answer: str, job_description: str) -> dict[str, Any]:
        score = 0.82 if answer else 0.25
        return {
            "score": score,
            "role_alignment": 0.78 if answer else 0.1,
            "strengths": ["Structured response", "Relevant examples"] if answer else [],
            "weaknesses": ["Could quantify impact more"],
            "missing_points": ["Explicit alignment to job requirements"],
            "suggestion": "Add concrete metrics and close with business impact.",
        }

    def answer_clarification(self, question: str) -> str:
        return f"I'm looking for a concise, example-driven answer to: {question}"

    def generate_feedback(self, transcript: str, evaluations: list[dict[str, Any]]) -> dict[str, Any]:
        avg_score = round(sum(item["score"] for item in evaluations) / max(len(evaluations), 1), 2)
        return {
            "summary": "Strong foundation with room to add clearer impact and tighter role alignment.",
            "overall_score": avg_score,
            "role_alignment": 0.78,
            "answer_quality": avg_score,
            "improvement_momentum": 0.3,
            "strengths": ["Good structure", "Solid technical reasoning"],
            "improvement_areas": ["Quantify outcomes", "Make company fit more explicit"],
            "prep_guidance": [
                "Practice 5 STAR stories with metrics.",
                "Prepare role-specific architecture examples.",
                "Review the job description and map answers to it.",
            ],
        }


class OpenAILLMProvider(LLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.openai_model
        self.client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    def _json_completion(self, prompt: str) -> dict[str, Any]:
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        )
        return json.loads(response.choices[0].message.content or "{}")

    def extract_job_metadata(self, raw_text: str, url: str) -> dict[str, Any]:
        template = (
            "Extract job posting details from the following content. Return JSON with these fields:\n"
            "- company_name (string): The ACTUAL hiring company, NOT the job board platform. "
            "Ignore platforms like Greenhouse, Lever, Workday, LinkedIn, Indeed, etc.\n"
            "- role_title (string): The job position title\n"
            "- job_description (string): Key responsibilities and requirements (max 1200 chars)\n"
            "- confidence (number): 0-1 score for extraction quality\n\n"
            "URL: {url}\n\n"
            "Content:\n{raw_text}"
        )
        return self._json_completion(PromptTemplate.from_template(template).format(url=url, raw_text=raw_text))

    def extract_questions(
        self,
        context: str,
        company_name: str = "",
        role_title: str = "",
        job_description: str = "",
    ) -> list[dict[str, Any]]:
        template = (
            "You are building a high-signal mock interview for a candidate.\n"
            "Generate 8 questions that are specific to the company, role, and job posting. "
            "Use the research context when it contains real interview patterns, but do not copy "
            "low-quality, generic, or SEO listicle questions. Prioritize realistic questions an "
            "interviewer would ask for this exact role.\n\n"
            "Rules:\n"
            "- Include a balanced mix of technical, system_design, behavioral, role_fit, and company_fit questions.\n"
            "- Make each question answerable in a voice interview in 60-120 seconds.\n"
            "- Tie questions to named responsibilities, technologies, products, customer problems, or evaluation signals when available.\n"
            "- Avoid generic questions like 'Tell me about yourself' unless rewritten around the role context.\n"
            "- Return JSON only: {{'questions': [{{'text': string, 'category': string, 'importance': number}}]}}.\n\n"
            "Company: {company_name}\n"
            "Role: {role_title}\n"
            "Job posting context:\n{job_description}\n\n"
            "Research context:\n{context}"
        )
        payload = self._json_completion(
            PromptTemplate.from_template(template).format(
                context=context[:6000],
                company_name=company_name,
                role_title=role_title,
                job_description=job_description[:3000],
            )
        )
        return payload.get("questions", [])

    def infer_questions_from_jd(self, company_name: str, role_title: str, job_description: str) -> list[dict[str, Any]]:
        template = (
            "Infer 8 strong, role-specific mock interview questions from this job description. "
            "Avoid generic questions; make each question reflect the responsibilities, required skills, "
            "and company context. "
            "Return {{'questions': [{{'text': string, 'category': string, 'importance': number}}]}}.\n"
            "Company: {company_name}\nRole: {role_title}\nJob Description:\n{job_description}"
        )
        payload = self._json_completion(
            PromptTemplate.from_template(template).format(company_name=company_name, role_title=role_title, job_description=job_description)
        )
        return payload.get("questions", [])

    def generate_answer_guide(self, question: str, job_description: str) -> str:
        template = (
            "Return {{'guide': '...'}} with a concise interviewer answer guide.\n"
            "Question: {question}\nJob Description: {job_description}"
        )
        payload = self._json_completion(PromptTemplate.from_template(template).format(question=question, job_description=job_description))
        return payload.get("guide", "")

    def evaluate_answer(self, question: str, answer: str, job_description: str) -> dict[str, Any]:
        template = (
            "You are evaluating a technical interview answer. Be strict and honest.\n\n"
            "VALIDATION RULES:\n"
            "1. Check if the answer actually addresses the question asked\n"
            "2. Empty, very short (< 10 words), or off-topic answers should score < 0.3\n"
            "3. Vague or generic answers without specifics should score 0.3-0.5\n"
            "4. Answers with some relevant details should score 0.5-0.7\n"
            "5. Strong, detailed, relevant answers should score 0.7-1.0\n\n"
            "Return JSON with these fields:\n"
            "- score (number 0-1): Quality score based on relevance and depth\n"
            "- role_alignment (number 0-1): How clearly the answer maps to the role, job requirements, company context, and question intent\n"
            "- strengths (array of strings): What was good about the answer (empty if poor)\n"
            "- weaknesses (array of strings): What was missing or wrong\n"
            "- missing_points (array of strings): Key points that should have been mentioned\n"
            "- suggestion (string): One specific improvement tip\n\n"
            "Question: {question}\n\n"
            "Answer: {answer}\n\n"
            "Job Context: {job_description}\n\n"
            "Evaluate honestly. If the answer is irrelevant or nonsensical, say so clearly."
        )
        return self._json_completion(
            PromptTemplate.from_template(template).format(question=question, answer=answer, job_description=job_description)
        )

    def answer_clarification(self, question: str) -> str:
        payload = self._json_completion(
            f"Return {{'clarification': '...'}} with a concise clarification for interview question: {question}"
        )
        return payload.get("clarification", "")

    def generate_feedback(self, transcript: str, evaluations: list[dict[str, Any]]) -> dict[str, Any]:
        template = (
            "You are an expert interview coach analyzing a technical interview.\n\n"
            "IMPORTANT VALIDATION RULES:\n"
            "1. Only analyze answers that directly respond to the questions asked\n"
            "2. Ignore empty, incomplete, or nonsensical responses\n"
            "3. If an answer is off-topic or doesn't address the question, note it as a weakness\n"
            "4. Base your summary ONLY on substantive question-answer pairs\n"
            "5. If there are fewer than 3 valid answers, note that the interview was incomplete\n\n"
            "Generate final interview feedback as JSON with these exact fields:\n"
            "- summary (string): 2-3 sentence overall assessment based on actual answers given\n"
            "- overall_score (number): 0-1 score (0.0-0.3 for incomplete/poor, 0.3-0.6 for average, 0.6-0.8 for good, 0.8-1.0 for excellent)\n"
            "- role_alignment (number): 0-1 score for how consistently answers map to the role requirements and company context\n"
            "- answer_quality (number): 0-1 score for answer relevance, specificity, structure, and depth\n"
            "- improvement_momentum (number): 0-1 score for whether later answers improved compared with earlier answers\n"
            "- strengths (array of strings): Specific strengths demonstrated in answers (cite examples)\n"
            "- improvement_areas (array of strings): Concrete areas needing improvement (cite examples)\n"
            "- prep_guidance (array of strings): 3-5 actionable preparation tips based on performance gaps\n\n"
            "Interview Transcript (Q: Question, A: Answer):\n{transcript}\n\n"
            "Individual Question Evaluations:\n{evaluations}\n\n"
            "Analyze the quality of each answer relative to its question. Generate honest, specific feedback."
        )
        return self._json_completion(
            PromptTemplate.from_template(template).format(transcript=transcript, evaluations=json.dumps(evaluations))
        )


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if not settings.openai_api_key:
        return MockLLMProvider()
    return OpenAILLMProvider()
