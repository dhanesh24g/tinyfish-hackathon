from __future__ import annotations

from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.agents.job_extraction_agent import JobExtractionAgent
from app.services.repositories import JobTargetRepository


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
        job_target = self.repo.create(url)
        if (
            job_target.status == "extracted"
            and job_target.company_name
            and job_target.role_title
            and job_target.raw_tinyfish_result
        ):
            return job_target

        try:
            fetched = self.agent.fetch_job_posting_with_tinyfish(url)
            metadata = self.agent.extract_job_metadata(url=url, raw_text=fetched["text"])
            raw_tinyfish_result = fetched["raw"]
            raw_page_text = fetched["text"]
            status = "extracted"
        except TimeoutError:
            metadata = self._fallback_metadata_from_url(url)
            raw_tinyfish_result = {
                "provider": "tinyfish_sdk",
                "url": url,
                "error": "timeout",
                "note": "TinyFish timed out; fell back to URL-derived metadata.",
            }
            raw_page_text = ""
            status = "extracted"

        return self.repo.update_extraction(
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

    def get_job_target(self, job_target_id: int):
        return self.repo.get(job_target_id)
