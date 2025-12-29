from __future__ import annotations

import logging

from provenance_feed.config import get_settings
from provenance_feed.ingestion.real_sources import fetch_all_records
from provenance_feed.ingestion.service import ingest_once
from provenance_feed.persistence.sqlite import SQLiteFeedRepository


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    settings = get_settings()
    repo = SQLiteFeedRepository(database_path=settings.database_path)
    repo.init_schema()
    records = fetch_all_records()
    count = ingest_once(repo=repo, records=records)
    print(f"Ingested {count} items")


if __name__ == "__main__":
    main()
