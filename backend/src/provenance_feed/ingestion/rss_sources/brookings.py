from __future__ import annotations

from provenance_feed.ingestion.rss_common import RSSSource, ingest_source

BROOKINGS_FEED = RSSSource(
    source_id="brookings",
    source_name="Brookings (Research/Commentary)",
    feed_url="https://www.brookings.edu/feed/",
)


def ingest(timeout_seconds: float = 10.0) -> list[dict]:
    return ingest_source(source=BROOKINGS_FEED, timeout_seconds=timeout_seconds)
