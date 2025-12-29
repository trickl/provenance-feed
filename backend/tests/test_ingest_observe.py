from __future__ import annotations

from datetime import UTC, datetime

from provenance_feed.domain.models import FeedItem
from provenance_feed.ingestion.service import ingest_once
from provenance_feed.provenance_graph.observer import ObserveContentPayload, ProvenanceGraphObserver


class _RepoStub:
    def __init__(self, *, fail_on_content_id: str | None = None) -> None:
        self.upserted: list[str] = []
        self._fail_on = fail_on_content_id

    def upsert(self, item: FeedItem) -> None:
        if self._fail_on and item.content_id == self._fail_on:
            raise RuntimeError("boom")
        self.upserted.append(item.content_id)


class _ObserverStub:
    def __init__(self) -> None:
        self.seen: list[str] = []

    def observe_content(self, *, item: FeedItem) -> None:
        self.seen.append(item.content_id)


def test_ingest_calls_observer_only_after_successful_upsert() -> None:
    records = [
        {
            "source": "mock",
            "source_item_id": "1",
            "published_at": "2025-01-01T12:00:00+00:00",
            "title": "A",
            "source_name": "Mock",
            "source_url": "https://example.com/1",
        },
        {
            "source": "mock",
            "source_item_id": "2",
            "published_at": "2025-01-01T12:01:00+00:00",
            "title": "B",
            "source_name": "Mock",
            "source_url": "https://example.com/2",
        },
    ]

    repo = _RepoStub(fail_on_content_id="mock:2")
    observer = _ObserverStub()

    try:
        ingest_once(repo=repo, records=records, observer=observer)
    except RuntimeError:
        pass

    assert repo.upserted == ["mock:1"]
    assert observer.seen == ["mock:1"]


def test_provenance_graph_observer_payload_is_exact() -> None:
    obs = ProvenanceGraphObserver(
        enabled=False,
        observe_url="http://127.0.0.1:8010/api/v1/observe/content",
        api_key=None,
    )

    item = FeedItem(
        content_id="bbc:xyz",
        title="Hello",
        source_name="BBC",
        source_url="https://example.com/story",
        published_at=datetime(2025, 1, 1, 12, 0, tzinfo=UTC),
    )

    payload = obs.build_payload(item=item)
    assert payload == ObserveContentPayload(
        content_id="bbc:xyz",
        canonical_url="https://example.com/story",
        title="Hello",
        published_at="2025-01-01T12:00:00+00:00",
        source_key="bbc",
        source_display_name="BBC",
    )
