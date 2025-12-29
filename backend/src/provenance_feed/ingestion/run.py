from __future__ import annotations

import logging

from provenance_feed.config import get_settings
from provenance_feed.ingestion.real_sources import fetch_all_records
from provenance_feed.ingestion.service import ingest_once
from provenance_feed.persistence.sqlite import SQLiteFeedRepository
from provenance_feed.provenance_graph.observer import ProvenanceGraphObserver


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    settings = get_settings()
    repo = SQLiteFeedRepository(database_path=settings.database_path)
    repo.init_schema()
    observer = ProvenanceGraphObserver(
        enabled=settings.provenance_graph_observe_enabled,
        observe_url=settings.provenance_graph_observe_url,
        api_key=settings.provenance_graph_write_api_key,
        timeout_seconds=settings.provenance_graph_observe_timeout_seconds,
        queue_size=settings.provenance_graph_observe_queue_size,
    )
    records = fetch_all_records()
    count = ingest_once(repo=repo, records=records, observer=observer)
    print(f"Ingested {count} items")


if __name__ == "__main__":
    main()
