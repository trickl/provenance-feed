from __future__ import annotations

import json
import logging
import queue
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from provenance_feed.domain.models import FeedItem

logger = logging.getLogger(__name__)


def source_key_from_content_id(content_id: str) -> str:
    # `make_content_id()` guarantees the format `source:source_item_id`.
    head, sep, _tail = content_id.partition(":")
    if sep and head:
        return head
    return "unknown"


@dataclass(frozen=True)
class ObserveContentPayload:
    content_id: str
    canonical_url: str
    title: str
    published_at: str
    source_key: str
    source_display_name: str


class ProvenanceGraphObserver:
    """Best-effort observer for provenance-graph.

    Design constraints (by intent):
    - Non-blocking for ingestion: enqueue (drop if queue full), send on a daemon thread.
    - No retries.
    - Failures are non-fatal: log and move on.

    This keeps provenance-feed sovereign and provenance-graph observational.
    """

    def __init__(
        self,
        *,
        enabled: bool,
        observe_url: str,
        api_key: str | None,
        timeout_seconds: float = 0.75,
        queue_size: int = 200,
    ) -> None:
        self._enabled = enabled
        self._observe_url = observe_url
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds
        self._queue: queue.Queue[ObserveContentPayload] = queue.Queue(maxsize=max(1, queue_size))

        self._thread: threading.Thread | None = None
        if self._enabled:
            if not self._observe_url:
                raise ValueError("observe_url must be non-empty when enabled")
            if not self._api_key:
                logger.warning(
                    "provenance-graph observation is enabled but no API key is configured; "
                    "requests will likely be rejected"
                )
            self._thread = threading.Thread(
                target=self._worker,
                name="provgraph-observer",
                daemon=True,
            )
            self._thread.start()

    @property
    def enabled(self) -> bool:
        return self._enabled

    def build_payload(self, *, item: FeedItem) -> ObserveContentPayload:
        published_at = FeedItem.ensure_utc(item.published_at).isoformat()
        return ObserveContentPayload(
            content_id=item.content_id,
            canonical_url=item.source_url,
            title=item.title,
            published_at=published_at,
            source_key=source_key_from_content_id(item.content_id),
            source_display_name=item.source_name,
        )

    def observe_content(self, *, item: FeedItem) -> None:
        """Queue an observe call (never blocks ingestion)."""

        if not self._enabled:
            return

        payload = self.build_payload(item=item)
        try:
            self._queue.put_nowait(payload)
        except queue.Full:
            # Best-effort only: if we can't enqueue without blocking, drop.
            logger.warning(
                "provenance-graph observer queue is full; dropping observe event for content_id=%s",
                item.content_id,
            )

    def _worker(self) -> None:
        while True:
            payload = self._queue.get()
            try:
                self._post_payload(payload)
            except Exception as e:
                # Never raise: observational only.
                logger.warning(
                    "provenance-graph observe failed for content_id=%s (%s); not retrying",
                    payload.content_id,
                    type(e).__name__,
                )
            finally:
                self._queue.task_done()

    def _post_payload(self, payload: ObserveContentPayload) -> None:
        body = json.dumps(
            {
                "content_id": payload.content_id,
                "canonical_url": payload.canonical_url,
                "title": payload.title,
                "published_at": payload.published_at,
                "source_key": payload.source_key,
                "source_display_name": payload.source_display_name,
            },
            ensure_ascii=False,
        ).encode("utf-8")

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["X-API-Key"] = self._api_key

        req = urllib.request.Request(self._observe_url, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self._timeout_seconds) as resp:
                status = getattr(resp, "status", 200)
                if status < 200 or status >= 300:
                    # Read a small body snippet for debugging.
                    raw = resp.read(4096)
                    snippet = raw.decode("utf-8", errors="replace")
                    raise RuntimeError(f"unexpected status {status}: {snippet}")
                # Drain a little to reuse connections where possible (best-effort).
                resp.read(1024)
        except urllib.error.HTTPError as e:
            # Include HTTP status without dumping huge bodies.
            try:
                snippet = e.read(4096).decode("utf-8", errors="replace")
            except Exception:
                snippet = ""
            raise RuntimeError(f"http {e.code}: {snippet}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"url error: {e.reason}") from e


def safe_observe(observer: Any, *, item: FeedItem) -> None:
    """Call an observer, swallowing errors.

    This is a second safety rail: even if a custom observer implementation is buggy,
    ingestion should not fail because of observational plumbing.
    """

    try:
        observer.observe_content(item=item)
    except Exception as e:
        logger.warning(
            "provenance-graph observe raised unexpectedly for content_id=%s (%s); ignoring",
            item.content_id,
            type(e).__name__,
        )
