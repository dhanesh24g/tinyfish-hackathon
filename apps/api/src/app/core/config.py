from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "apps/api/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "TinyFish AI Mock Interview"
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    backend_api_key: str | None = Field(default=None, alias="BACKEND_API_KEY")
    backend_cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="BACKEND_CORS_ORIGINS",
    )

    database_url: str = Field(default="sqlite:///./tinyfish_ai.db", alias="DATABASE_URL")
    sqlite_fallback_url: str = Field(default="sqlite:///./tinyfish_ai.db", alias="SQLITE_FALLBACK_URL")

    @field_validator("database_url", mode="after")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Normalize PostgreSQL URLs to use psycopg2 dialect.
        
        SQLAlchemy defaults to psycopg3 for 'postgresql://' URLs,
        but we use psycopg2-binary. This validator ensures compatibility.
        """
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        elif v.startswith("postgresql+psycopg://"):
            return v.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
        return v

    supabase_url: str | None = Field(default=None, alias="SUPABASE_URL")
    supabase_anon_key: str | None = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str | None = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")

    tinyfish_api_key: str | None = Field(default=None, alias="TINYFISH_API_KEY")
    tinyfish_base_url: str = Field(default="https://api.tinyfish.ai", alias="TINYFISH_BASE_URL")
    tinyfish_timeout_seconds: int = Field(default=60, alias="TINYFISH_TIMEOUT_SECONDS")  # Per TinyFish docs: browser sessions take 10-30s
    tinyfish_stealth: bool = Field(default=True, alias="TINYFISH_STEALTH")
    tinyfish_use_mock: bool = Field(default=True, alias="TINYFISH_USE_MOCK")

    def validate_runtime(self) -> None:
        if self.app_env != "production":
            return

        issues: list[str] = []
        if self.debug:
            issues.append("DEBUG must be false in production.")
        if self.tinyfish_use_mock:
            issues.append("TINYFISH_USE_MOCK must be false in production.")
        if not self.tinyfish_api_key:
            issues.append("TINYFISH_API_KEY is required in production.")
        if not self.openai_api_key:
            issues.append("OPENAI_API_KEY is required in production.")
        if self.database_url.startswith("sqlite"):
            issues.append("DATABASE_URL must point to Postgres in production.")

        if issues:
            raise ValueError("Invalid production configuration: " + " ".join(issues))


@lru_cache
def get_settings() -> Settings:
    return Settings()
