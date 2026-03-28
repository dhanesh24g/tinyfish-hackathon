from __future__ import annotations

import json
from typing import Any

from langchain_core.prompts import PromptTemplate
from openai import OpenAI

from app.core.config import get_settings


class LLMProvider:
    def extract_job_metadata(self, raw_text: str, url: str) -> dict[str, Any]:
        raise NotImplementedError

    def extract_questions(self, context: str) -> list[dict[str, Any]]:
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

    def extract_questions(self, context: str) -> list[dict[str, Any]]:
        return [
            {"text": "Tell me about yourself.", "category": "behavioral", "importance": 0.95},
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
        prompt = PromptTemplate.from_template(
            "Extract company_name, role_title, job_description, confidence from this job posting for {url}:\n{raw_text}"
        )
        return self._json_completion(prompt.format(url=url, raw_text=raw_text))

    def extract_questions(self, context: str) -> list[dict[str, Any]]:
        prompt = PromptTemplate.from_template(
            "Extract interview questions from the following research context. "
            "Return {{'questions': [{{'text': ..., 'category': ..., 'importance': 0-1}}]}}.\n{context}"
        )
        payload = self._json_completion(prompt.format(context=context))
        return payload.get("questions", [])

    def infer_questions_from_jd(self, company_name: str, role_title: str, job_description: str) -> list[dict[str, Any]]:
        prompt = PromptTemplate.from_template(
            "Infer likely interview questions from this job description. "
            "Return {{'questions': [{{'text': ..., 'category': ..., 'importance': 0-1}}]}}.\n"
            "Company: {company_name}\nRole: {role_title}\nJob Description:\n{job_description}"
        )
        payload = self._json_completion(
            prompt.format(company_name=company_name, role_title=role_title, job_description=job_description)
        )
        return payload.get("questions", [])

    def generate_answer_guide(self, question: str, job_description: str) -> str:
        prompt = PromptTemplate.from_template(
            "Return {{'guide': '...'}} with a concise interviewer answer guide.\n"
            "Question: {question}\nJob Description: {job_description}"
        )
        payload = self._json_completion(prompt.format(question=question, job_description=job_description))
        return payload.get("guide", "")

    def evaluate_answer(self, question: str, answer: str, job_description: str) -> dict[str, Any]:
        prompt = PromptTemplate.from_template(
            "Evaluate the answer and return JSON with score, strengths, weaknesses, missing_points, suggestion.\n"
            "Question: {question}\nAnswer: {answer}\nJob Description: {job_description}"
        )
        return self._json_completion(
            prompt.format(question=question, answer=answer, job_description=job_description)
        )

    def answer_clarification(self, question: str) -> str:
        payload = self._json_completion(
            f"Return {{'clarification': '...'}} with a concise clarification for interview question: {question}"
        )
        return payload.get("clarification", "")

    def generate_feedback(self, transcript: str, evaluations: list[dict[str, Any]]) -> dict[str, Any]:
        prompt = PromptTemplate.from_template(
            "Generate final interview feedback. Return summary, overall_score, strengths, improvement_areas, prep_guidance.\n"
            "Transcript:\n{transcript}\nEvaluations:\n{evaluations}"
        )
        return self._json_completion(
            prompt.format(transcript=transcript, evaluations=json.dumps(evaluations))
        )


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if not settings.openai_api_key:
        return MockLLMProvider()
    return OpenAILLMProvider()
