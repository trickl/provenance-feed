from __future__ import annotations

from datetime import datetime
from typing import Protocol

from provenance_feed.domain.identifiers import make_content_id
from provenance_feed.domain.models import FeedItem
from provenance_feed.persistence.repository import FeedRepository
from provenance_feed.provenance_graph.observer import safe_observe

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

    image_last_checked = raw.get("image_last_checked")
    if image_last_checked:
        try:
            image_last_checked_dt = FeedItem.ensure_utc(datetime.fromisoformat(image_last_checked))
        except Exception:
            image_last_checked_dt = None
    else:
        image_last_checked_dt = None

    return FeedItem(
        content_id=content_id,
        title=raw["title"].strip(),
        source_name=raw["source_name"].strip(),
        source_url=raw["source_url"].strip(),
        published_at=published_at,
        image_url=(raw.get("image_url") or None),
        image_source=(raw.get("image_source") or None),
        image_last_checked=image_last_checked_dt,
    )


class ContentObserver(Protocol):
    def observe_content(self, *, item: FeedItem) -> None: ...


def ingest_once(
    *,
    repo: FeedRepository,
    records: list[dict],
    observer: ContentObserver | None = None,
) -> int:
    """Ingest and persist records. Returns number of items upserted."""

    items = [normalise_record(r) for r in records]
    for item in items:
        repo.upsert(item)
        # Best-effort, non-blocking observational hook.
        if observer is not None:
            safe_observe(observer, item=item)
    return len(items)
