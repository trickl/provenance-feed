from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from provenance_feed.api.routes.feed import router as feed_router
from provenance_feed.config import Settings, get_settings
from provenance_feed.ingestion.mock_source import fetch_mock_items
from provenance_feed.ingestion.service import ingest_once
from provenance_feed.persistence.sqlite import SQLiteFeedRepository


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    repo = SQLiteFeedRepository(database_path=settings.database_path)
    repo.init_schema()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Optional convenience for local development only.
        if settings.auto_ingest_on_startup:
            ingest_once(repo=repo, records=fetch_mock_items())
        yield

    app = FastAPI(title="provenance-feed", version="0.1.0", lifespan=lifespan)

    app.state.settings = settings
    app.state.repo = repo

    origins = [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=False,
            allow_methods=["GET"],
            allow_headers=["*"],
        )

    app.include_router(feed_router)

    @app.get("/healthz")
    def healthz() -> dict:
        return {"ok": True}

    return app
