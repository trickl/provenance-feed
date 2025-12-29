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

    # Optional: best-effort observation hook into provenance-graph.
    # The feed must remain sovereign: observation failures are non-fatal.
    provenance_graph_observe_enabled: bool = False
    provenance_graph_observe_url: str = "http://127.0.0.1:8010/api/v1/observe/content"
    provenance_graph_write_api_key: str | None = None
    provenance_graph_observe_timeout_seconds: float = 0.75
    provenance_graph_observe_queue_size: int = 200


def get_settings() -> Settings:
    return Settings()
