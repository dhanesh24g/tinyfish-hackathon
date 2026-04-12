from __future__ import annotations

import logging

from app.providers.llm_provider import LLMProvider
from app.providers.tinyfish_provider import TinyFishProvider

logger = logging.getLogger(__name__)


class JobExtractionAgent:
    def __init__(self, tinyfish: TinyFishProvider, llm: LLMProvider) -> None:
        self.tinyfish = tinyfish
        self.llm = llm

    def fetch_job_posting_with_tinyfish(self, url: str) -> dict:
        result = self.tinyfish.fetch_page(url)
        return {"url": url, "raw": result.raw, "text": result.text, "metadata": result.metadata}

    def extract_job_metadata(self, url: str, raw_text: str, tinyfish_metadata: dict | None = None) -> dict:
        """Extract job metadata, preferring TinyFish's extraction if available."""
        # If TinyFish already extracted metadata, use it (it's more accurate for structured data)
        if tinyfish_metadata and tinyfish_metadata.get("company_name"):
            logger.info(f"[HOP:METADATA_SRC] Using TinyFish metadata | company={tinyfish_metadata.get('company_name')} role={tinyfish_metadata.get('role_title')}")
            return {
                "company_name": tinyfish_metadata.get("company_name"),
                "role_title": tinyfish_metadata.get("role_title"),
                "job_description": tinyfish_metadata.get("job_description", raw_text[:1200]),
                "confidence": tinyfish_metadata.get("confidence", 0.9),
            }
        # Fallback to LLM extraction if TinyFish didn't provide metadata
        logger.warning(f"[HOP:METADATA_SRC] Falling back to LLM extraction | company_name missing in TinyFish response | url={url}")
        return self.llm.extract_job_metadata(raw_text=raw_text, url=url)
