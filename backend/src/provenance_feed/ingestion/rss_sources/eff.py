from __future__ import annotations

from provenance_feed.ingestion.rss_common import RSSSource, ingest_source

EFF_UPDATES = RSSSource(
    source_id="eff",
    source_name="EFF (Updates)",
    feed_url="https://www.eff.org/rss/updates.xml",
)


def ingest(timeout_seconds: float = 10.0) -> list[dict]:
    return ingest_source(source=EFF_UPDATES, timeout_seconds=timeout_seconds)
