from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agents.evaluation_agent import EvaluationAgent
from app.agents.interview_agent import InterviewAgent
from app.models.interview import InterviewSession
from app.models.job_target import JobTarget
from app.services.repositories import EvaluationRepository, InterviewRepository, QuestionRepository


class InterviewService:
    def __init__(self, db: Session, interview_agent: InterviewAgent, evaluation_agent: EvaluationAgent) -> None:
        self.db = db
        self.interview_agent = interview_agent
        self.evaluation_agent = evaluation_agent
        self.repo = InterviewRepository(db)
        self.question_repo = QuestionRepository(db)
        self.evaluation_repo = EvaluationRepository(db)

    def start_session(self, job_target: JobTarget, mode: str) -> InterviewSession:
        session = self.repo.create_session(job_target.id, mode, datetime.now(timezone.utc))
        starting = self.interview_agent.starting_prompt()
        self.repo.add_turn(session.id, None, 0, starting, "system_prompt", datetime.now(timezone.utc))
        session.current_question_index = 0
        return self.repo.update_session(session)

    def handle_event(self, session: InterviewSession, job_target: JobTarget, event_type: str, payload: str | None):
        questions = self.question_repo.list_by_job_target(job_target.id)
        normalized = self.interview_agent.normalize_event_payload(event_type, payload)
        answered_turn_count = sum(1 for turn in session.turns if turn.user_response is not None)
        is_intro_answer = answered_turn_count == 0 and bool(session.turns)

        if event_type == "clarification_request":
            current_prompt = session.turns[-1].agent_prompt if session.turns else self.interview_agent.starting_prompt()
            self.repo.add_turn(
                session.id,
                None,
                len(session.turns),
                self.interview_agent.answer_clarification(current_prompt),
                event_type,
                datetime.now(timezone.utc),
            )
            session = self.repo.update_session(session)
            return session

        if event_type == "stop_interview":
            return self.stop_session(session, "user_requested_stop")

        if is_intro_answer:
            current_question = session.turns[0].agent_prompt
            question_id = None
        else:
            question = questions[min(session.current_question_index, max(len(questions) - 1, 0))] if questions else None
            current_question = question.text if question else self.interview_agent.starting_prompt()
            question_id = question.id if question else None

        answer_turn = self.repo.add_turn(
            session.id,
            question_id,
            len(session.turns),
            current_question,
            event_type,
            datetime.now(timezone.utc),
            user_response=normalized,
        )
        evaluation = self.evaluation_agent.evaluate_answer(current_question, normalized, job_target.job_description or "")
        self.evaluation_repo.create_evaluation(
            {
                "session_id": session.id,
                "turn_id": answer_turn.id,
                "score": evaluation["score"],
                "strengths": evaluation["strengths"],
                "weaknesses": evaluation["weaknesses"],
                "missing_points": evaluation["missing_points"],
                "suggestion": evaluation.get("suggestion"),
                "raw_payload": evaluation,
                "created_at": datetime.now(timezone.utc),
            }
        )

        next_index = session.current_question_index if is_intro_answer else session.current_question_index + 1
        session.current_question_index = next_index
        if next_index < len(questions):
            next_question = questions[next_index].text
            self.repo.add_turn(
                session.id,
                questions[next_index].id,
                len(session.turns) + 1,
                next_question,
                "agent_question",
                datetime.now(timezone.utc),
            )
        else:
            session.status = "completed"
            session.ended_at = datetime.now(timezone.utc)
        return self.repo.update_session(session)

    def stop_session(self, session: InterviewSession, reason: str):
        session.status = "stopped"
        session.stop_reason = reason
        session.ended_at = datetime.now(timezone.utc)
        return self.repo.update_session(session)
