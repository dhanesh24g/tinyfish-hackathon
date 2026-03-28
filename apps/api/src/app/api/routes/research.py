from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_services
from app.schemas.research import ResearchRunRequest, ResearchRunResponse
from app.services.container import ServiceContainer
from app.services.repositories import JobTargetRepository

router = APIRouter()


@router.post("/run", response_model=None)
def run_research(
    payload: ResearchRunRequest,
    db: Session = Depends(get_db),
    services: ServiceContainer = Depends(get_services),
):
    repos = JobTargetRepository(db)
    job_target = repos.get(payload.job_target_id)
    if not job_target:
        raise HTTPException(status_code=404, detail="Job target not found")
    research_service = services.with_db(db)["research_service"]
    if payload.stream:
        return StreamingResponse(research_service.stream(job_target), media_type="text/event-stream")
    sources, questions = research_service.run(job_target)
    return ResearchRunResponse(job_target_id=job_target.id, sources=sources, questions=questions)
