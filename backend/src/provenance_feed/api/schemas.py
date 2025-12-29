from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class FeedItemOut(BaseModel):
    content_id: str = Field(..., description="Stable identifier (used for provenance lookup later)")
    title: str
    source_name: str
    source_url: str
    published_at: datetime
