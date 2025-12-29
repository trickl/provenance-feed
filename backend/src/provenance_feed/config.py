from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend configuration.

    Environment variables are prefixed with BACKEND_.
    """

    model_config = SettingsConfigDict(
        env_prefix="BACKEND_",
        extra="ignore",
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
    )

    database_path: Path = Path("backend/data/feed.db")
    auto_ingest_on_startup: bool = True
    cors_allow_origins: str = "http://localhost:5173,http://127.0.0.1:5173"


def get_settings() -> Settings:
    return Settings()
