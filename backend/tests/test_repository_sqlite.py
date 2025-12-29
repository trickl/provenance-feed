from datetime import UTC, datetime

from provenance_feed.domain.models import FeedItem
from provenance_feed.persistence.sqlite import SQLiteFeedRepository


def test_sqlite_repo_upsert_and_list_latest(tmp_path) -> None:
    db = tmp_path / "feed.db"
    repo = SQLiteFeedRepository(database_path=db)
    repo.init_schema()

    a = FeedItem(
        content_id="mock:1",
        title="A",
        source_name="Mock",
        source_url="https://example.com/1",
        published_at=datetime(2025, 1, 1, 12, 0, tzinfo=UTC),
    )
    b = FeedItem(
        content_id="mock:2",
        title="B",
        source_name="Mock",
        source_url="https://example.com/2",
        published_at=datetime(2025, 1, 1, 13, 0, tzinfo=UTC),
    )

    repo.upsert(a)
    repo.upsert(b)

    items = repo.list_latest(limit=10)
    assert [i.content_id for i in items] == ["mock:2", "mock:1"]
