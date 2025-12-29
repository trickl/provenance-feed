from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class FeedItem(BaseModel):
    """Canonical internal model for an item in the feed."""

    content_id: str = Field(..., description="Stable identifier used for provenance lookups")
    title: str
    source_name: str
    source_url: str
    published_at: datetime

    @staticmethod
    def ensure_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
