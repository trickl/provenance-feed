from __future__ import annotations

from provenance_feed.ingestion.rss_common import RSSSource, ingest_source

RELIEFWEB_UPDATES = RSSSource(
    source_id="reliefweb",
    source_name="ReliefWeb (Updates)",
    feed_url="https://reliefweb.int/updates/rss.xml",
)


def ingest(timeout_seconds: float = 10.0) -> list[dict]:
    return ingest_source(source=RELIEFWEB_UPDATES, timeout_seconds=timeout_seconds)
