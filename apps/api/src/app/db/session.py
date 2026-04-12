from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_engine():
    """Lazy engine creation - only called when database is actually used."""
    settings = get_settings()
    database_url = settings.database_url or settings.sqlite_fallback_url

    # Convert psycopg3 (postgresql+psycopg) to psycopg2 (postgresql+psycopg2) if needed
    if "postgresql+psycopg" in database_url and "psycopg2" not in database_url:
        database_url = database_url.replace("postgresql+psycopg", "postgresql+psycopg2")
    if database_url.startswith("postgresql://") and not database_url.startswith("postgresql+psycopg"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    engine_kwargs = {
        "future": True,
        "pool_pre_ping": True,
    }

    # Supabase transaction pooler should not sit behind a long-lived SQLAlchemy pool,
    # especially on serverless runtimes like Vercel.
    if ".pooler.supabase.com" in database_url:
        engine_kwargs["poolclass"] = NullPool

    return create_engine(database_url, **engine_kwargs)


@lru_cache(maxsize=1)
def get_session_local():
    """Lazy sessionmaker creation."""
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, expire_on_commit=False)


def SessionLocal():
    """Factory function that returns a new session - lazy evaluation."""
    return get_session_local()()


class _LazyEngine:
    """Lazy proxy for engine that only creates it on first use."""
    _engine = None

    def __getattr__(self, name):
        if self._engine is None:
            self._engine = get_engine()
        return getattr(self._engine, name)

    def __setattr__(self, name, value):
        if name == "_engine":
            super().__setattr__(name, value)
        else:
            if self._engine is None:
                self._engine = get_engine()
            setattr(self._engine, name, value)


# Module-level engine - lazy evaluated on first use
engine = _LazyEngine()
