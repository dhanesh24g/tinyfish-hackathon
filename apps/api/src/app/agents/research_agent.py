from __future__ import annotations

import re
from urllib.parse import quote_plus

from app.providers.tinyfish_provider import TinyFishProvider


class ResearchAgent:
    def __init__(self, tinyfish: TinyFishProvider) -> None:
        self.tinyfish = tinyfish

    def _important_terms(self, job_description: str) -> list[str]:
        known_terms = [
            "python",
            "fastapi",
            "postgres",
            "sql",
            "aws",
            "kubernetes",
            "react",
            "typescript",
            "machine learning",
            "llm",
            "rag",
            "distributed systems",
            "system design",
            "data pipeline",
        ]
        description = job_description.lower()
        matched = [term for term in known_terms if term in description]
        if matched:
            return matched[:4]

        words = re.findall(r"[A-Za-z][A-Za-z+#.-]{2,}", job_description)
        stop_words = {
            "and",
            "are",
            "for",
            "the",
            "with",
            "you",
            "our",
            "will",
            "that",
            "this",
            "from",
            "have",
            "work",
            "team",
            "role",
        }
        unique: list[str] = []
        for word in words:
            normalized = word.lower()
            if normalized in stop_words or normalized in unique:
                continue
            unique.append(normalized)
            if len(unique) == 4:
                break
        return unique

    def build_queries(self, company_name: str, role_title: str, job_description: str = "") -> list[str]:
        """Build targeted search queries for interview research.
        
        Uses specific keywords to find:
        1. Company-specific interview questions
        2. Candidate experiences and patterns
        3. Role-specific technical questions
        """
        company = company_name.strip() or "target company"
        role = role_title.strip() or "target role"
        skill_terms = " ".join(self._important_terms(job_description))

        def google_search(query: str) -> str:
            return f"https://www.google.com/search?q={quote_plus(query)}"
        
        return [
            # Company + role specific questions
            google_search(f'"{company}" "{role}" interview questions Glassdoor LeetCode'),
            # Company interview experiences
            google_search(f'"{company}" interview experience "{role}" Reddit Blind'),
            # Role-specific technical questions (fallback if company is generic)
            google_search(f'"{role}" technical interview questions {skill_terms}'.strip()),
        ]

    async def fetch_research_sources_with_tinyfish(self, urls: list[str]) -> list[dict]:
        results = await self.tinyfish.fetch_many_async(urls, goal=getattr(self.tinyfish, "research_goal", None))
        documents: list[dict] = []
        for item in results:
            status = item.raw.get("fetch_status") or item.raw.get("status") or "completed"
            documents.append(
                {
                    "url": item.url,
                    "text": item.text if status == "completed" else "",
                    "raw": item.raw,
                    "fetch_status": status,
                }
            )
        return documents
