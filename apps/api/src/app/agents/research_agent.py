from __future__ import annotations

from app.providers.tinyfish_provider import TinyFishProvider


class ResearchAgent:
    def __init__(self, tinyfish: TinyFishProvider) -> None:
        self.tinyfish = tinyfish

    def build_queries(self, company_name: str, role_title: str) -> list[str]:
        """Build targeted search queries for interview research.
        
        Uses specific keywords to find:
        1. Company-specific interview questions
        2. Candidate experiences and patterns
        3. Role-specific technical questions
        """
        # Sanitize inputs for URL encoding
        company = company_name.strip().replace(" ", "+")
        role = role_title.strip().replace(" ", "+")
        
        return [
            # Company + role specific questions
            f"https://www.google.com/search?q={company}+{role}+interview+questions+site:glassdoor.com+OR+site:leetcode.com",
            # Company interview experiences
            f"https://www.google.com/search?q={company}+interview+experience+{role}+site:reddit.com+OR+site:blind.com",
            # Role-specific technical questions (fallback if company is generic)
            f"https://www.google.com/search?q={role}+technical+interview+questions+2026",
        ]

    async def fetch_research_sources_with_tinyfish(self, urls: list[str]) -> list[dict]:
        results = await self.tinyfish.fetch_many_async(urls, goal=getattr(self.tinyfish, "research_goal", None))
        return [{"url": item.url, "text": item.text, "raw": item.raw} for item in results]
