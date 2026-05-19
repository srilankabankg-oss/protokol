"""Application configuration via pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql+asyncpg://protokol:protokol_secret@localhost:5432/protokol"
    database_url_sync: str = "postgresql://protokol:protokol_secret@localhost:5432/protokol"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT Authentication
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # LLM Gateway
    llm_gateway_url: str = "http://localhost:8001"
    llm_api_key: Optional[str] = None
    llm_base_url: str = "https://api.stepfun.com/step_plan/v1"
    llm_model: str = "step-router-v1"
    llm_timeout: int = 180

    # App
    debug: bool = False
    app_name: str = "Protokol API"
    app_version: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()