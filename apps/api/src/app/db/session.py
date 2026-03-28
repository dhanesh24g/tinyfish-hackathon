from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()
database_url = settings.database_url or settings.sqlite_fallback_url
engine_kwargs = {
    "future": True,
    "pool_pre_ping": True,
}

# Supabase transaction pooler should not sit behind a long-lived SQLAlchemy pool,
# especially on serverless runtimes like Vercel.
if ".pooler.supabase.com" in database_url:
    engine_kwargs["poolclass"] = NullPool
    # PgBouncer transaction pooling does not support psycopg prepared statements.
    engine_kwargs["connect_args"] = {"prepare_threshold": None}

engine = create_engine(
    database_url,
    **engine_kwargs,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
