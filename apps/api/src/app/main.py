from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    settings.validate_runtime()
    if settings.app_env == "local":
        init_db()
    yield


settings = get_settings()
cors_origins = [item.strip() for item in settings.backend_cors_origins.split(",") if item.strip()]
app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
