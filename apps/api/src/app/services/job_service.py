from __future__ import annotations

import time
from urllib.parse import urlparse

import logging

from sqlalchemy.orm import Session

from app.agents.job_extraction_agent import JobExtractionAgent
from app.services.repositories import JobTargetRepository

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self, db: Session, agent: JobExtractionAgent) -> None:
        self.db = db
        self.agent = agent
        self.repo = JobTargetRepository(db)

    def create_job_target(self, url: str):
        return self.repo.create(url)

    def _fallback_metadata_from_url(self, url: str) -> dict:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        company_name = hostname.split(".")[-2].title() if "." in hostname else hostname.title()

        slug = parsed.path.rstrip("/").split("/")[-1] if parsed.path else ""
        slug_parts = [part for part in slug.split("-") if part and not part.isdigit()]
        if slug_parts and slug_parts[0].isdigit():
            slug_parts = slug_parts[1:]
        role_title = " ".join(part.capitalize() for part in slug_parts) or "Target Role"

        if "google." in hostname:
            company_name = "Google"

        return {
            "company_name": company_name or None,
            "role_title": role_title,
            "job_description": f"Timed out extracting the full job page for {role_title}. Using URL-derived metadata.",
            "confidence": 0.3,
        }

    def extract_job_target(self, url: str):
        t0 = time.time()

        # HOP 1: DB lookup/create
        job_target = self.repo.create(url)
        logger.info(f"[HOP:DB_CREATE] job_target created/fetched | {time.time() - t0:.1f}s")

        if (
            job_target.status == "extracted"
            and job_target.company_name
            and job_target.role_title
            and job_target.raw_tinyfish_result
        ):
            logger.info(f"[HOP:CACHE_HIT] Returning cached | company={job_target.company_name} role={job_target.role_title} | {time.time() - t0:.1f}s")
            return job_target

        # HOP 2: TinyFish web scrape
        t1 = time.time()
        try:
            fetched = self.agent.fetch_job_posting_with_tinyfish(url)
            logger.info(f"[HOP:TINYFISH_DONE] Scrape complete | {time.time() - t1:.1f}s")

            # HOP 3: Metadata extraction
            t2 = time.time()
            metadata = self.agent.extract_job_metadata(
                url=url, 
                raw_text=fetched["text"],
                tinyfish_metadata=fetched.get("raw")
            )
            logger.info(f"[HOP:METADATA] company={metadata.get('company_name')} role={metadata.get('role_title')} | {time.time() - t2:.1f}s")
            raw_tinyfish_result = fetched["raw"]
            raw_page_text = fetched["text"]
            status = "extracted"
        except TimeoutError:
            logger.warning(f"[HOP:TINYFISH_TIMEOUT] Timed out after {time.time() - t1:.1f}s | url={url}")
            metadata = self._fallback_metadata_from_url(url)
            raw_tinyfish_result = {
                "provider": "tinyfish_sdk",
                "url": url,
                "error": "timeout",
                "note": "TinyFish timed out; fell back to URL-derived metadata.",
            }
            raw_page_text = ""
            status = "extracted"
        except Exception as e:
            logger.exception(f"[HOP:TINYFISH_ERR] {type(e).__name__} after {time.time() - t1:.1f}s | {e}")
            metadata = self._fallback_metadata_from_url(url)
            raw_tinyfish_result = {
                "provider": "tinyfish_sdk",
                "url": url,
                "error": str(type(e).__name__),
                "note": f"Extraction failed: {str(e)}",
            }
            raw_page_text = ""
            status = "extracted"

        # HOP 4: DB save
        t3 = time.time()
        result = self.repo.update_extraction(
            job_target,
            {
                "company_name": metadata.get("company_name"),
                "role_title": metadata.get("role_title"),
                "job_description": metadata.get("job_description"),
                "confidence": metadata.get("confidence"),
                "raw_tinyfish_result": raw_tinyfish_result,
                "raw_page_text": raw_page_text,
                "status": status,
            },
        )
        logger.info(f"[HOP:DB_SAVE] Extraction saved | {time.time() - t3:.1f}s | total={time.time() - t0:.1f}s")
        return result

    def get_job_target(self, job_target_id: int):
        return self.repo.get(job_target_id)
