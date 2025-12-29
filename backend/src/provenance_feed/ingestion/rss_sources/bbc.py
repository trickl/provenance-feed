from __future__ import annotations

from provenance_feed.ingestion.rss_common import RSSSource, ingest_source

BBC_WORLD = RSSSource(
    source_id="bbc",
    source_name="BBC News (World)",
    feed_url="https://feeds.bbci.co.uk/news/world/rss.xml",
)


def ingest(timeout_seconds: float = 10.0) -> list[dict]:
    return ingest_source(source=BBC_WORLD, timeout_seconds=timeout_seconds)
