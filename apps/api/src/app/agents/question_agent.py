from __future__ import annotations

from collections import OrderedDict
import logging
import re

from app.providers.llm_provider import LLMProvider
from app.utils.scoring import compute_question_score

logger = logging.getLogger(__name__)


class QuestionAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def _build_research_context(self, raw_documents: list[dict]) -> str:
        snippets: list[str] = []
        for item in raw_documents:
            if item.get("fetch_status") not in (None, "completed"):
                continue
            text = str(item.get("text") or "").strip()
            if not text:
                continue
            snippets.append(f"Source: {item.get('url', 'unknown')}\n{text[:1600]}")
        return "\n\n".join(snippets)

    def extract_questions(
        self,
        raw_documents: list[dict],
        company_name: str = "",
        role_title: str = "",
        job_description: str = "",
    ) -> list[dict]:
        context = self._build_research_context(raw_documents)
        if not context and not job_description:
            return []
        try:
            return self.llm.extract_questions(
                context,
                company_name=company_name,
                role_title=role_title,
                job_description=job_description,
            )
        except Exception:
            logger.exception("Question extraction failed; falling back to job-description questions.")
            return []

    def fallback_questions(self, company_name: str, role_title: str, job_description: str) -> list[dict]:
        try:
            questions = self.llm.infer_questions_from_jd(company_name, role_title, job_description)
        except Exception:
            logger.exception("LLM fallback question generation failed; using local fallback questions.")
            questions = self._local_fallback_questions(company_name, role_title, job_description)
        for item in questions:
            item["is_fallback"] = True
        return questions

    def _local_fallback_questions(
        self,
        company_name: str,
        role_title: str,
        job_description: str,
    ) -> list[dict]:
        company = company_name or "this company"
        role = role_title or "this role"
        terms = re.findall(r"[A-Za-z][A-Za-z+#.-]{3,}", job_description)
        keyword_text = ", ".join(dict.fromkeys(terms[:5])) or "the listed responsibilities"
        return [
            {
                "text": f"Which parts of your background best prepare you for the {role} responsibilities at {company}?",
                "category": "role_fit",
                "importance": 0.86,
            },
            {
                "text": f"How would you approach the first 90 days in this {role} role?",
                "category": "role_fit",
                "importance": 0.82,
            },
            {
                "text": f"Tell me about a project where you used skills related to {keyword_text}.",
                "category": "behavioral",
                "importance": 0.8,
            },
            {
                "text": f"What technical tradeoffs would you expect to discuss for a {role} position?",
                "category": "technical",
                "importance": 0.78,
            },
        ]

    def rank_questions(self, questions: list[dict], company_name: str, role_title: str) -> list[dict]:
        deduped: dict[str, dict] = OrderedDict()
        role_terms = {
            term
            for term in re.findall(r"[a-zA-Z][a-zA-Z+#.-]{2,}", role_title.lower())
            if term not in {"and", "the", "for", "with"}
        }
        generic_openers = (
            "tell me about yourself",
            "why should we hire you",
            "what are your strengths",
            "what are your weaknesses",
        )
        for item in questions:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text") or "").strip()
            if not text:
                continue
            key = text.lower()
            if key not in deduped:
                frequency = min(1.0, 0.5 + 0.1 * len(deduped))
                recency = 0.7
                role_hits = sum(1 for term in role_terms if term in key)
                relevance = min(1.0, 0.72 + (0.08 * role_hits))
                if company_name and company_name.lower() in key:
                    relevance = min(1.0, relevance + 0.08)
                if any(key.startswith(opener) for opener in generic_openers):
                    relevance = max(0.45, relevance - 0.25)
                try:
                    importance = float(item.get("importance", 0.75))
                except (TypeError, ValueError):
                    importance = 0.75
                importance = max(0.0, min(1.0, importance))
                item["text"] = text
                item["frequency_score"] = frequency
                item["recency_score"] = recency
                item["relevance_score"] = relevance
                item["importance_score"] = importance
                item["final_score"] = compute_question_score(frequency, recency, relevance, importance)
                item["rationale"] = f"Ranked for {company_name} / {role_title} relevance."
                deduped[key] = item
        return sorted(deduped.values(), key=lambda item: item["final_score"], reverse=True)
