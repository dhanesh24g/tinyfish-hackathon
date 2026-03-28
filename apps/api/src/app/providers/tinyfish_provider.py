from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import httpx
from bs4 import BeautifulSoup
from readability import Document
import trafilatura

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class TinyFishResult:
    url: str
    html: str
    text: str
    metadata: dict[str, Any]
    raw: dict[str, Any]


class TinyFishProvider:
    def fetch_page(self, url: str) -> TinyFishResult:
        raise NotImplementedError

    async def fetch_page_async(self, url: str) -> TinyFishResult:
        raise NotImplementedError

    async def fetch_many_async(self, urls: list[str]) -> list[TinyFishResult]:
        raise NotImplementedError

    async def stream_progress(self, urls: list[str]):
        raise NotImplementedError


class MockTinyFishProvider(TinyFishProvider):
    def fetch_page(self, url: str) -> TinyFishResult:
        html = f"""
        <html>
          <head><title>Senior Backend Engineer at TinyFish Labs</title></head>
          <body>
            <h1>Senior Backend Engineer</h1>
            <div class="company">TinyFish Labs</div>
            <div class="description">
              Build reliable Python backend services, orchestration workflows, SQL systems,
              and collaborate with product teams.
            </div>
          </body>
        </html>
        """
        text = "Senior Backend Engineer at TinyFish Labs. Build reliable Python backend services."
        return TinyFishResult(
            url=url,
            html=html,
            text=text,
            metadata={"title": "Senior Backend Engineer at TinyFish Labs"},
            raw={"provider": "mock_tinyfish", "url": url, "html": html, "text": text},
        )

    async def fetch_page_async(self, url: str) -> TinyFishResult:
        await asyncio.sleep(0.35)
        return self.fetch_page(url)

    async def fetch_many_async(self, urls: list[str]) -> list[TinyFishResult]:
        return [await self.fetch_page_async(url) for url in urls]

    async def stream_progress(self, urls: list[str]):
        for index, url in enumerate(urls, start=1):
            result = await self.fetch_page_async(url)
            await asyncio.sleep(0.8)
            yield {"index": index, "total": len(urls), "url": url, "status": "completed", "result": result.raw}


class HttpTinyFishProvider(TinyFishProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.timeout = httpx.Timeout(self.settings.tinyfish_timeout_seconds)
        self.headers = {"Authorization": f"Bearer {self.settings.tinyfish_api_key}"}

    def _post_process(self, url: str, raw: dict[str, Any]) -> TinyFishResult:
        html = raw.get("html") or raw.get("content") or ""
        extracted = trafilatura.extract(html) if html else None
        if not extracted and html:
            extracted = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
        if html:
            readable = Document(html).summary(html_partial=True)
            readable_text = BeautifulSoup(readable, "html.parser").get_text(" ", strip=True)
            extracted = extracted or readable_text
        return TinyFishResult(
            url=url,
            html=html,
            text=extracted or raw.get("text", ""),
            metadata=raw.get("metadata", {}),
            raw=raw,
        )

    def fetch_page(self, url: str) -> TinyFishResult:
        with httpx.Client(base_url=self.settings.tinyfish_base_url, timeout=self.timeout) as client:
            response = client.post(
                "/v1/browser/fetch",
                headers=self.headers,
                json={
                    "url": url,
                    "render_js": True,
                    "stealth": self.settings.tinyfish_stealth,
                    "return_html": True,
                    "return_text": True,
                },
            )
            response.raise_for_status()
            return self._post_process(url, response.json())

    async def fetch_page_async(self, url: str) -> TinyFishResult:
        async with httpx.AsyncClient(base_url=self.settings.tinyfish_base_url, timeout=self.timeout) as client:
            response = await client.post(
                "/v1/browser/fetch",
                headers=self.headers,
                json={
                    "url": url,
                    "render_js": True,
                    "stealth": self.settings.tinyfish_stealth,
                    "return_html": True,
                    "return_text": True,
                },
            )
            response.raise_for_status()
            return self._post_process(url, response.json())

    async def fetch_many_async(self, urls: list[str]) -> list[TinyFishResult]:
        return await asyncio.gather(*(self.fetch_page_async(url) for url in urls))

    async def stream_progress(self, urls: list[str]):
        for index, url in enumerate(urls, start=1):
            try:
                result = await self.fetch_page_async(url)
                yield {"index": index, "total": len(urls), "url": url, "status": "completed", "result": result.raw}
            except Exception as exc:  # pragma: no cover
                logger.exception("TinyFish fetch failed for %s", url)
                yield {"index": index, "total": len(urls), "url": url, "status": "failed", "error": str(exc)}


def get_tinyfish_provider() -> TinyFishProvider:
    settings = get_settings()
    if settings.tinyfish_use_mock:
        return MockTinyFishProvider()
    if not settings.tinyfish_api_key:
        raise ValueError("TINYFISH_API_KEY is required when TINYFISH_USE_MOCK is false.")
    return HttpTinyFishProvider()
