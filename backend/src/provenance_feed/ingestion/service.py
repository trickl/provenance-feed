from __future__ import annotations

from datetime import datetime

from provenance_feed.domain.identifiers import make_content_id
from provenance_feed.domain.models import FeedItem
from provenance_feed.persistence.repository import FeedRepository

"""Ingestion services.

Ingestion is intentionally minimal and lossy.

The feed is a consumer surface and does not attempt to preserve all upstream metadata
or to mirror source schemas. We only keep what is required for:

- display (title, source, timestamp, URL)
- stable identification (content_id)

This boundary helps prevent ingestion from quietly turning into a data warehouse.
"""


def normalise_record(raw: dict) -> FeedItem:
    """Normalise a raw ingestion record into the canonical FeedItem model."""

    content_id = make_content_id(source=raw["source"], source_item_id=raw["source_item_id"])
    published_at = datetime.fromisoformat(raw["published_at"])
    published_at = FeedItem.ensure_utc(published_at)
    return FeedItem(
        content_id=content_id,
        title=raw["title"].strip(),
        source_name=raw["source_name"].strip(),
        source_url=raw["source_url"].strip(),
        published_at=published_at,
    )


def ingest_once(*, repo: FeedRepository, records: list[dict]) -> int:
    """Ingest and persist records. Returns number of items upserted."""

    items = [normalise_record(r) for r in records]
    for item in items:
        repo.upsert(item)
    return len(items)
