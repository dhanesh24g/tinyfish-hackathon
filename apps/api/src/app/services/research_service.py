from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator

from sqlalchemy.orm import Session

from app.agents.question_agent import QuestionAgent
from app.agents.research_agent import ResearchAgent
from app.models.job_target import JobTarget
from app.services.repositories import QuestionRepository, SourceRepository


class ResearchService:
    def __init__(self, db: Session, research_agent: ResearchAgent, question_agent: QuestionAgent) -> None:
        self.db = db
        self.research_agent = research_agent
        self.question_agent = question_agent
        self.source_repo = SourceRepository(db)
        self.question_repo = QuestionRepository(db)

    def run(self, job_target: JobTarget):
        queries = self.research_agent.build_queries(job_target.company_name or "", job_target.role_title or "")
        documents = asyncio.run(self.research_agent.fetch_research_sources_with_tinyfish(queries))
        sources = self.source_repo.replace_for_job_target(job_target.id, documents)
        questions = self.question_agent.extract_questions(documents)
        if not questions:
            questions = self.question_agent.fallback_questions(
                company_name=job_target.company_name or "",
                role_title=job_target.role_title or "",
                job_description=job_target.job_description or "",
            )
        ranked = self.question_agent.rank_questions(
            questions,
            company_name=job_target.company_name or "",
            role_title=job_target.role_title or "",
        )
        saved_questions = self.question_repo.replace_for_job_target(job_target.id, ranked)
        return sources, saved_questions

    async def stream(self, job_target: JobTarget) -> AsyncGenerator[str, None]:
        queries = self.research_agent.build_queries(job_target.company_name or "", job_target.role_title or "")
        documents: list[dict] = []
        async for update in self.research_agent.tinyfish.stream_progress(queries):
            if update.get("status") == "completed":
                documents.append(
                    {
                        "url": update.get("url", ""),
                        "text": (update.get("result") or {}).get("text", ""),
                        "raw": update.get("result"),
                    }
                )
            yield f"data: {json.dumps({'type': 'progress', **update})}\n\n"

        sources = self.source_repo.replace_for_job_target(job_target.id, documents)
        questions = self.question_agent.extract_questions(documents)
        if not questions:
            questions = self.question_agent.fallback_questions(
                company_name=job_target.company_name or "",
                role_title=job_target.role_title or "",
                job_description=job_target.job_description or "",
            )
        ranked = self.question_agent.rank_questions(
            questions,
            company_name=job_target.company_name or "",
            role_title=job_target.role_title or "",
        )
        saved_questions = self.question_repo.replace_for_job_target(job_target.id, ranked)
        yield (
            "data: "
            + json.dumps(
                {
                    "type": "complete",
                    "job_target_id": job_target.id,
                    "source_count": len(sources),
                    "question_count": len(saved_questions),
                }
            )
            + "\n\n"
        )
