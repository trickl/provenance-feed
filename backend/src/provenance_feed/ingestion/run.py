from __future__ import annotations

from provenance_feed.config import get_settings
from provenance_feed.ingestion.mock_source import fetch_mock_items
from provenance_feed.ingestion.service import ingest_once
from provenance_feed.persistence.sqlite import SQLiteFeedRepository


def main() -> None:
    settings = get_settings()
    repo = SQLiteFeedRepository(database_path=settings.database_path)
    repo.init_schema()
    count = ingest_once(repo=repo, records=fetch_mock_items())
    print(f"Ingested {count} items")


if __name__ == "__main__":
    main()
