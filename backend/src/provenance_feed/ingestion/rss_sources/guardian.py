from __future__ import annotations

from provenance_feed.ingestion.rss_common import RSSSource, ingest_source

GUARDIAN_WORLD = RSSSource(
    source_id="guardian",
    source_name="The Guardian (World)",
    feed_url="https://www.theguardian.com/world/rss",
)


def ingest(timeout_seconds: float = 10.0) -> list[dict]:
    return ingest_source(source=GUARDIAN_WORLD, timeout_seconds=timeout_seconds)
