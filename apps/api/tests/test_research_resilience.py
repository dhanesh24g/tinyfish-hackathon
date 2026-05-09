import asyncio

from app.agents.question_agent import QuestionAgent
from app.agents.research_agent import ResearchAgent
from app.providers.tinyfish_provider import TinyFishResult


class PartiallyFailingTinyFish:
    research_goal = "research"

    async def fetch_many_async(self, urls: list[str], goal: str | None = None):
        return [
            TinyFishResult(
                url=urls[0],
                html="",
                text="Candidates report system design and FastAPI reliability questions.",
                metadata={},
                raw={"fetch_status": "completed"},
            ),
            TinyFishResult(
                url=urls[1],
                html="",
                text="This should not be used.",
                metadata={},
                raw={"fetch_status": "failed", "error": "upstream failure"},
            ),
        ]


class RecordingLLM:
    def __init__(self) -> None:
        self.context = ""
        self.company_name = ""
        self.role_title = ""
        self.job_description = ""

    def extract_questions(
        self,
        context: str,
        company_name: str = "",
        role_title: str = "",
        job_description: str = "",
    ):
        self.context = context
        self.company_name = company_name
        self.role_title = role_title
        self.job_description = job_description
        return [
            {
                "text": "How would you improve API reliability for this backend role?",
                "category": "technical",
                "importance": 0.9,
            }
        ]


class FailingLLM:
    def extract_questions(self, *args, **kwargs):
        raise RuntimeError("quota exceeded")

    def infer_questions_from_jd(self, *args, **kwargs):
        raise RuntimeError("quota exceeded")


def test_research_agent_keeps_successful_results_when_one_source_fails():
    agent = ResearchAgent(PartiallyFailingTinyFish())

    documents = asyncio.run(agent.fetch_research_sources_with_tinyfish(["https://one.test", "https://two.test"]))

    assert documents[0]["fetch_status"] == "completed"
    assert "FastAPI reliability" in documents[0]["text"]
    assert documents[1]["fetch_status"] == "failed"
    assert documents[1]["text"] == ""


def test_question_agent_uses_job_context_and_ignores_failed_research_text():
    llm = RecordingLLM()
    agent = QuestionAgent(llm)

    questions = agent.extract_questions(
        [
            {"url": "https://ok.test", "text": "Ask about FastAPI reliability.", "fetch_status": "completed"},
            {"url": "https://bad.test", "text": "Blocked page content.", "fetch_status": "failed"},
        ],
        company_name="TinyFish Labs",
        role_title="Senior Backend Engineer",
        job_description="Build reliable Python backend services with FastAPI and Postgres.",
    )

    assert questions
    assert "FastAPI reliability" in llm.context
    assert "Blocked page content" not in llm.context
    assert llm.company_name == "TinyFish Labs"
    assert llm.role_title == "Senior Backend Engineer"
    assert "Postgres" in llm.job_description


def test_question_agent_has_local_fallback_when_llm_generation_fails():
    agent = QuestionAgent(FailingLLM())

    questions = agent.fallback_questions(
        company_name="TinyFish Labs",
        role_title="Senior Backend Engineer",
        job_description="Build reliable Python backend services with FastAPI and Postgres.",
    )

    assert len(questions) >= 4
    assert all(question["is_fallback"] for question in questions)
    assert any("Senior Backend Engineer" in question["text"] for question in questions)
