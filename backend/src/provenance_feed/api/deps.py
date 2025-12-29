from __future__ import annotations

from fastapi import Request

from provenance_feed.config import Settings
from provenance_feed.persistence.repository import FeedRepository


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_repo(request: Request) -> FeedRepository:
    return request.app.state.repo
