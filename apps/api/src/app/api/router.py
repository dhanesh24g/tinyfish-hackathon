from fastapi import APIRouter, Depends

from app.api.routes.evaluation import router as evaluation_router
from app.api.routes.health import router as health_router
from app.api.routes.interview import router as interview_router
from app.api.routes.job_targets import router as job_target_router
from app.api.routes.question_bank import router as question_bank_router
from app.api.routes.research import router as research_router
from app.core.security import require_api_key

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(
    job_target_router,
    prefix="/job-targets",
    tags=["job-targets"],
    dependencies=[Depends(require_api_key)],
)
api_router.include_router(
    research_router,
    prefix="/research",
    tags=["research"],
    dependencies=[Depends(require_api_key)],
)
api_router.include_router(
    question_bank_router,
    prefix="/question-bank",
    tags=["question-bank"],
    dependencies=[Depends(require_api_key)],
)
api_router.include_router(
    interview_router,
    prefix="/interview",
    tags=["interview"],
    dependencies=[Depends(require_api_key)],
)
api_router.include_router(
    evaluation_router,
    prefix="/evaluation",
    tags=["evaluation"],
    dependencies=[Depends(require_api_key)],
)
