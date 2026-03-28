from __future__ import annotations

from app.providers.tinyfish_provider import TinyFishProvider


class ResearchAgent:
    def __init__(self, tinyfish: TinyFishProvider) -> None:
        self.tinyfish = tinyfish

    def build_queries(self, company_name: str, role_title: str) -> list[str]:
        return [
            f"https://www.google.com/search?q={company_name}+{role_title}+interview+questions",
            f"https://www.google.com/search?q={company_name}+engineering+interview+experience",
            f"https://www.google.com/search?q={role_title}+system+design+interview+questions",
        ]

    async def fetch_research_sources_with_tinyfish(self, urls: list[str]) -> list[dict]:
        results = await self.tinyfish.fetch_many_async(urls, goal=getattr(self.tinyfish, "research_goal", None))
        return [{"url": item.url, "text": item.text, "raw": item.raw} for item in results]
