from __future__ import annotations

from typing import Protocol

from provenance_feed.domain.models import FeedItem


class FeedRepository(Protocol):
    def init_schema(self) -> None: ...

    def upsert(self, item: FeedItem) -> None: ...

    def list_latest(self, *, limit: int = 50) -> list[FeedItem]: ...
