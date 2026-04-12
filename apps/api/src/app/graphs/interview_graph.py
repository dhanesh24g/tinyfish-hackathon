from __future__ import annotations

import asyncio
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.evaluation_agent import EvaluationAgent
from app.agents.job_extraction_agent import JobExtractionAgent
from app.agents.question_agent import QuestionAgent
from app.agents.research_agent import ResearchAgent
from app.graphs.state import InterviewGraphState


class InterviewWorkflow:
    def __init__(
        self,
        job_agent: JobExtractionAgent,
        research_agent: ResearchAgent,
        question_agent: QuestionAgent,
        evaluation_agent: EvaluationAgent,
    ) -> None:
        self.job_agent = job_agent
        self.research_agent = research_agent
        self.question_agent = question_agent
        self.evaluation_agent = evaluation_agent
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(InterviewGraphState)
        graph.add_node("fetch_job_posting_with_tinyfish", self.fetch_job_posting_with_tinyfish)
        graph.add_node("extract_job_metadata", self.extract_job_metadata)
        graph.add_node("fetch_research_sources_with_tinyfish", self.fetch_research_sources_with_tinyfish)
        graph.add_node("extract_questions", self.extract_questions)
        graph.add_node("rank_questions", self.rank_questions)
        graph.add_node("run_interview", self.run_interview)
        graph.add_node("evaluate_answers", self.evaluate_answers)
        graph.add_node("generate_report", self.generate_report)

        graph.set_entry_point("fetch_job_posting_with_tinyfish")
        graph.add_edge("fetch_job_posting_with_tinyfish", "extract_job_metadata")
        graph.add_edge("extract_job_metadata", "fetch_research_sources_with_tinyfish")
        graph.add_edge("fetch_research_sources_with_tinyfish", "extract_questions")
        graph.add_edge("extract_questions", "rank_questions")
        graph.add_edge("rank_questions", "run_interview")
        graph.add_edge("run_interview", "evaluate_answers")
        graph.add_edge("evaluate_answers", "generate_report")
        graph.add_edge("generate_report", END)
        return graph.compile()

    def fetch_job_posting_with_tinyfish(self, state: InterviewGraphState) -> InterviewGraphState:
        result = self.job_agent.fetch_job_posting_with_tinyfish(state["job_posting_url"])
        return {
            "raw_tinyfish_job_extraction_output": result["raw"],
            "extracted_job_metadata": {"raw_text": result["text"], "metadata": result["metadata"]},
        }

    def extract_job_metadata(self, state: InterviewGraphState) -> InterviewGraphState:
        # Pass TinyFish metadata to avoid re-processing and ensure correct company extraction
        tinyfish_raw = state.get("raw_tinyfish_job_extraction_output")
        metadata = self.job_agent.extract_job_metadata(
            url=state["job_posting_url"],
            raw_text=state["extracted_job_metadata"]["raw_text"],
            tinyfish_metadata=tinyfish_raw,
        )
        return {"extracted_job_metadata": metadata}

    def fetch_research_sources_with_tinyfish(self, state: InterviewGraphState) -> InterviewGraphState:
        company_name = state["extracted_job_metadata"].get("company_name", "")
        role_title = state["extracted_job_metadata"].get("role_title", "")
        queries = self.research_agent.build_queries(company_name, role_title)
        documents = asyncio.run(self.research_agent.fetch_research_sources_with_tinyfish(queries))
        return {"raw_research_documents": documents}

    def extract_questions(self, state: InterviewGraphState) -> InterviewGraphState:
        questions = self.question_agent.extract_questions(state.get("raw_research_documents", []))
        if not questions:
            metadata = state["extracted_job_metadata"]
            questions = self.question_agent.fallback_questions(
                company_name=metadata.get("company_name", ""),
                role_title=metadata.get("role_title", ""),
                job_description=metadata.get("job_description", ""),
            )
        return {"question_bank": questions}

    def rank_questions(self, state: InterviewGraphState) -> InterviewGraphState:
        metadata = state["extracted_job_metadata"]
        ranked = self.question_agent.rank_questions(
            state.get("question_bank", []),
            company_name=metadata.get("company_name", ""),
            role_title=metadata.get("role_title", ""),
        )
        return {"question_bank": ranked}

    def run_interview(self, state: InterviewGraphState) -> InterviewGraphState:
        return {"interview_session_state": {"status": "prepared", "question_count": len(state.get("question_bank", []))}}

    def evaluate_answers(self, state: InterviewGraphState) -> InterviewGraphState:
        return {"evaluations": state.get("evaluations", [])}

    def generate_report(self, state: InterviewGraphState) -> InterviewGraphState:
        transcript = "\n".join(item.get("answer", "") for item in state.get("answers", []))
        report = self.evaluation_agent.generate_report(transcript=transcript, evaluations=state.get("evaluations", []))
        return {"final_report": report}

    def invoke(self, state: InterviewGraphState) -> InterviewGraphState:
        return self.graph.invoke(state)
