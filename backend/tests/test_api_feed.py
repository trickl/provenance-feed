from fastapi.testclient import TestClient

from provenance_feed.api.app import create_app
from provenance_feed.config import Settings


def test_feed_endpoint_returns_list(tmp_path) -> None:
    settings = Settings(database_path=tmp_path / "feed.db", auto_ingest_on_startup=True)
    app = create_app(settings)
    client = TestClient(app)
    r = client.get("/api/feed")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        assert "content_id" in data[0]
        assert "title" in data[0]
        assert "source_name" in data[0]
        assert "published_at" in data[0]
