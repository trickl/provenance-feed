from __future__ import annotations

from datetime import UTC, datetime, timedelta


def fetch_mock_items() -> list[dict]:
    """Placeholder ingestion source.

    Returns a small, deterministic set of mock records.
    """

    # Deterministic timestamps keep tests and local dev predictable.
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    return [
        {
            "source": "mock",
            "source_item_id": "1",
            "title": "A minimal feed scaffold",
            "source_name": "Mock Source",
            "source_url": "https://example.com/mock/1",
            "published_at": (now - timedelta(minutes=20)).isoformat(),
        },
        {
            "source": "mock",
            "source_item_id": "2",
            "title": "Clean boundaries beat cleverness",
            "source_name": "Mock Source",
            "source_url": "https://example.com/mock/2",
            "published_at": (now - timedelta(minutes=10)).isoformat(),
        },
        {
            "source": "mock",
            "source_item_id": "3",
            "title": "Reserved space for provenance (not implemented)",
            "source_name": "Mock Source",
            "source_url": "https://example.com/mock/3",
            "published_at": now.isoformat(),
        },
    ]
