from __future__ import annotations

from provenance_feed.ingestion.rss_common import RSSSource, ingest_source

NASA_BREAKING = RSSSource(
    source_id="nasa",
    source_name="NASA (Breaking News)",
    feed_url="https://www.nasa.gov/rss/dyn/breaking_news.rss",
)


def ingest(timeout_seconds: float = 10.0) -> list[dict]:
    return ingest_source(source=NASA_BREAKING, timeout_seconds=timeout_seconds)
