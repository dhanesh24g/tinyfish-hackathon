from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import json
import logging
from dataclasses import dataclass
from typing import Any

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
    def fetch_page(self, url: str, goal: str | None = None) -> TinyFishResult:
        raise NotImplementedError

    async def fetch_page_async(self, url: str, goal: str | None = None) -> TinyFishResult:
        raise NotImplementedError

    async def fetch_many_async(self, urls: list[str], goal: str | None = None) -> list[TinyFishResult]:
        raise NotImplementedError

    async def stream_progress(self, urls: list[str], goal: str | None = None):
        raise NotImplementedError


class MockTinyFishProvider(TinyFishProvider):
    def fetch_page(self, url: str, goal: str | None = None) -> TinyFishResult:
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

    async def fetch_page_async(self, url: str, goal: str | None = None) -> TinyFishResult:
        await asyncio.sleep(0.35)
        return self.fetch_page(url, goal=goal)

    async def fetch_many_async(self, urls: list[str], goal: str | None = None) -> list[TinyFishResult]:
        return [await self.fetch_page_async(url, goal=goal) for url in urls]

    async def stream_progress(self, urls: list[str], goal: str | None = None):
        for index, url in enumerate(urls, start=1):
            result = await self.fetch_page_async(url, goal=goal)
            await asyncio.sleep(0.8)
            yield {"index": index, "total": len(urls), "url": url, "status": "completed", "result": result.raw}


class HttpTinyFishProvider(TinyFishProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        try:
            from tinyfish import TinyFish
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "TinyFish SDK is not installed. Run `pip install tinyfish>=0.2.5`."
            ) from exc

        # Initialize TinyFish SDK
        # Note: Timeout is handled at the wrapper level via ThreadPoolExecutor
        # The SDK doesn't expose a timeout parameter in its constructor
        self.client = TinyFish(api_key=self.settings.tinyfish_api_key)
        self.job_extraction_goal = (
            "Open this job page and extract the job posting details. Return a structured JSON object with exactly these fields: "
            "title, company_name (the ACTUAL hiring company, NOT the job board like Greenhouse/Lever/LinkedIn), "
            "role_title, job_description, confidence, text, html. "
            "Keep job_description concise, max 1200 characters. "
            "Confidence must be a number between 0 and 1. "
            "Focus on the main job content, ignore platform metadata and navigation elements. "
            "Do not browse beyond what is necessary on this page."
        )
        self.research_goal = (
            "Quickly extract interview-relevant information from this page. Return a structured JSON object with: "
            "title, text, html. Keep text concise, max 1000 characters, focusing on interview questions, "
            "candidate experiences, or role-relevant evaluation signals. Do not spend time on unrelated content."
        )

    def _coerce_event(self, event: Any) -> dict[str, Any]:
        if isinstance(event, dict):
            return event
        if hasattr(event, "model_dump"):
            return event.model_dump()
        if hasattr(event, "dict"):
            return event.dict()
        if hasattr(event, "__dict__"):
            return dict(event.__dict__)
        return {"value": str(event)}

    def _check_for_failure_signals(self, result: dict[str, Any]) -> bool:
        """Check if TinyFish result contains failure signals.
        
        Per TinyFish docs: COMPLETED status doesn't mean success.
        Check for: captcha, blocked, access denied, etc.
        """
        result_str = str(result).lower()
        failure_signals = ["captcha", "blocked", "access denied", "forbidden", "rate limit", "cloudflare"]
        return any(signal in result_str for signal in failure_signals)
    
    def _extract_payload(self, url: str, events: list[dict[str, Any]]) -> dict[str, Any]:
        raw: dict[str, Any] = {}
        for event in events:
            for key in ("resultJson", "result_json", "result", "data", "output"):
                candidate = event.get(key)
                if isinstance(candidate, dict):
                    raw.update(candidate)
                elif isinstance(candidate, str):
                    try:
                        parsed = json.loads(candidate)
                    except json.JSONDecodeError:
                        parsed = None
                    if isinstance(parsed, dict):
                        raw.update(parsed)
            if not raw and event.get("type") in {"final", "complete", "completed"}:
                raw.update(event)

        if "text" not in raw:
            raw["text"] = " ".join(
                str(event.get("message") or event.get("text") or "").strip()
                for event in events
                if event.get("message") or event.get("text")
            ).strip()
        if "html" not in raw:
            raw["html"] = ""
        raw.setdefault("url", url)
        return raw

    def _post_process(self, url: str, raw: dict[str, Any]) -> TinyFishResult:
        html = raw.get("html") or raw.get("content") or ""
        extracted = None

        # Try trafilatura first
        if html:
            try:
                extracted = trafilatura.extract(html)
            except Exception:
                pass

        # Fallback to BeautifulSoup
        if not extracted and html:
            try:
                extracted = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
            except Exception:
                pass

        # Try readability
        if html:
            try:
                readable = Document(html).summary(html_partial=True)
                readable_text = BeautifulSoup(readable, "html.parser").get_text(" ", strip=True)
                extracted = extracted or readable_text
            except Exception:
                pass

        return TinyFishResult(
            url=url,
            html=html,
            text=extracted or raw.get("text", "") or raw.get("job_description", ""),
            metadata={
                "title": raw.get("title"),
                "company_name": raw.get("company_name"),
                "role_title": raw.get("role_title"),
                **(raw.get("metadata", {}) if isinstance(raw.get("metadata"), dict) else {}),
            },
            raw=raw,
        )

    def _run_agent(self, url: str, goal: str) -> list[dict[str, Any]]:
        def _collect() -> list[dict[str, Any]]:
            collected: list[dict[str, Any]] = []
            with self.client.agent.stream(url=url, goal=goal) as stream:
                for event in stream:
                    collected.append(self._coerce_event(event))
            return collected

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_collect)
            try:
                return future.result(timeout=self.settings.tinyfish_timeout_seconds)
            except FutureTimeoutError as exc:
                future.cancel()
                raise TimeoutError(
                    f"TinyFish timed out after {self.settings.tinyfish_timeout_seconds}s for {url}"
                ) from exc

    def fetch_page(self, url: str, goal: str | None = None) -> TinyFishResult:
        events: list[dict[str, Any]] = []
        events.extend(self._run_agent(url, goal or self.job_extraction_goal))
        payload = self._extract_payload(url, events)
        
        # Check for failure signals per TinyFish docs
        if self._check_for_failure_signals(payload):
            logger.warning("TinyFish detected failure signals (captcha/blocked) for %s", url)
        
        return self._post_process(url, payload)

    async def fetch_page_async(self, url: str, goal: str | None = None) -> TinyFishResult:
        return await asyncio.to_thread(self.fetch_page, url, goal)

    async def fetch_many_async(self, urls: list[str], goal: str | None = None) -> list[TinyFishResult]:
        return await asyncio.gather(*(self.fetch_page_async(url, goal=goal) for url in urls))

    async def stream_progress(self, urls: list[str], goal: str | None = None):
        for index, url in enumerate(urls, start=1):
            try:
                events: list[dict[str, Any]] = []
                events.extend(self._run_agent(url, goal or self.research_goal))
                for payload in events:
                    yield {
                        "index": index,
                        "total": len(urls),
                        "url": url,
                        "status": str(payload.get("type") or "running"),
                        "event": payload,
                    }
                result = self._post_process(url, self._extract_payload(url, events))
                yield {"index": index, "total": len(urls), "url": url, "status": "completed", "result": result.raw}
            except TimeoutError as exc:  # Specific timeout handling
                logger.warning("TinyFish timeout for %s after %ds", url, self.settings.tinyfish_timeout_seconds)
                yield {
                    "index": index,
                    "total": len(urls),
                    "url": url,
                    "status": "timeout",
                    "error": f"Timeout after {self.settings.tinyfish_timeout_seconds}s",
                }
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
