from __future__ import annotations

from provenance_feed.ingestion.rss_common import RSSSource, ingest_source

NPR_NEWS = RSSSource(
    source_id="npr",
    source_name="NPR (News)",
    feed_url="https://feeds.npr.org/1001/rss.xml",
)


def ingest(timeout_seconds: float = 10.0) -> list[dict]:
    return ingest_source(source=NPR_NEWS, timeout_seconds=timeout_seconds)
