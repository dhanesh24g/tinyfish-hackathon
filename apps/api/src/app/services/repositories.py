from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.evaluation import Evaluation, EvaluationRun, FeedbackReport
from app.models.interview import InterviewSession, InterviewTurn
from app.models.job_target import JobTarget
from app.models.question import Question
from app.models.source import Source


class JobTargetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, url: str) -> JobTarget:
        existing = self.db.scalar(select(JobTarget).where(JobTarget.job_posting_url == url))
        if existing:
            return existing
        item = JobTarget(job_posting_url=url)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, job_target_id: int) -> JobTarget | None:
        return self.db.get(JobTarget, job_target_id)

    def update_extraction(self, item: JobTarget, payload: dict) -> JobTarget:
        item.company_name = payload.get("company_name")
        item.role_title = payload.get("role_title")
        item.job_description = payload.get("job_description")
        item.extraction_confidence = payload.get("confidence")
        item.raw_tinyfish_result = payload.get("raw_tinyfish_result")
        item.raw_page_text = payload.get("raw_page_text")
        item.status = payload.get("status", item.status)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item


class SourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def replace_for_job_target(self, job_target_id: int, documents: list[dict]) -> list[Source]:
        try:
            self.db.query(Source).filter(Source.job_target_id == job_target_id).delete(synchronize_session=False)
            items = [
                Source(
                    job_target_id=job_target_id,
                    source_url=document["url"],
                    source_type="research",
                    raw_tinyfish_result=document.get("raw"),
                    parsed_text=document.get("text"),
                    fetch_status="completed",
                )
                for document in documents
            ]
            self.db.add_all(items)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        for item in items:
            self.db.refresh(item)
        return items

    def list_by_job_target(self, job_target_id: int) -> list[Source]:
        return list(self.db.scalars(select(Source).where(Source.job_target_id == job_target_id)))


class QuestionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def replace_for_job_target(self, job_target_id: int, questions: list[dict]) -> list[Question]:
        try:
            self.db.query(Question).filter(Question.job_target_id == job_target_id).delete(synchronize_session=False)
            items = [
                Question(
                    job_target_id=job_target_id,
                    text=question["text"],
                    category=question.get("category"),
                    frequency_score=question.get("frequency_score", 0),
                    recency_score=question.get("recency_score", 0),
                    relevance_score=question.get("relevance_score", 0),
                    importance_score=question.get("importance_score", 0),
                    final_score=question.get("final_score", 0),
                    rationale=question.get("rationale"),
                    is_fallback=question.get("is_fallback", False),
                )
                for question in questions
            ]
            self.db.add_all(items)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        for item in items:
            self.db.refresh(item)
        return items

    def list_by_job_target(self, job_target_id: int) -> list[Question]:
        stmt = select(Question).where(Question.job_target_id == job_target_id).order_by(Question.final_score.desc())
        return list(self.db.scalars(stmt))


class InterviewRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(self, job_target_id: int, mode: str, started_at) -> InterviewSession:
        session = InterviewSession(job_target_id=job_target_id, mode=mode, started_at=started_at)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: int) -> InterviewSession | None:
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(selectinload(InterviewSession.turns), selectinload(InterviewSession.evaluations))
        )
        return self.db.scalar(stmt)

    def add_turn(self, session_id: int, question_id: int | None, turn_index: int, agent_prompt: str, event_type: str, created_at, user_response: str | None = None) -> InterviewTurn:
        turn = InterviewTurn(
            session_id=session_id,
            question_id=question_id,
            turn_index=turn_index,
            agent_prompt=agent_prompt,
            user_response=user_response,
            event_type=event_type,
            created_at=created_at,
        )
        self.db.add(turn)
        self.db.commit()
        self.db.refresh(turn)
        return turn

    def update_session(self, session: InterviewSession) -> InterviewSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return self.get_session(session.id)


class EvaluationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_evaluation(self, payload: dict) -> Evaluation:
        item = Evaluation(**payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def upsert_feedback(self, payload: dict) -> FeedbackReport:
        existing = self.db.scalar(select(FeedbackReport).where(FeedbackReport.session_id == payload["session_id"]))
        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            item = existing
        else:
            item = FeedbackReport(**payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_run(self, payload: dict) -> EvaluationRun:
        item = EvaluationRun(**payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
