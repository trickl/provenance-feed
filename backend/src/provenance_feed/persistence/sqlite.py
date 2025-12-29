from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from provenance_feed.domain.models import FeedItem
from provenance_feed.persistence.repository import FeedRepository


class SQLiteFeedRepository(FeedRepository):
    def __init__(self, *, database_path: Path):
        self._database_path = database_path

    def _connect(self) -> sqlite3.Connection:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self._database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feed_items (
                  content_id TEXT PRIMARY KEY,
                  title TEXT NOT NULL,
                  source_name TEXT NOT NULL,
                  source_url TEXT NOT NULL,
                  published_at TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                """
            )

    def upsert(self, item: FeedItem) -> None:
        now = datetime.now(tz=UTC).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO feed_items (
                  content_id, title, source_name, source_url, published_at, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(content_id) DO UPDATE SET
                  title=excluded.title,
                  source_name=excluded.source_name,
                  source_url=excluded.source_url,
                  published_at=excluded.published_at;
                """,
                (
                    item.content_id,
                    item.title,
                    item.source_name,
                    item.source_url,
                    FeedItem.ensure_utc(item.published_at).isoformat(),
                    now,
                ),
            )

    def list_latest(self, *, limit: int = 50) -> list[FeedItem]:
        if limit <= 0:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT content_id, title, source_name, source_url, published_at
                FROM feed_items
                ORDER BY published_at DESC
                LIMIT ?;
                """,
                (limit,),
            ).fetchall()

        return [
            FeedItem(
                content_id=r["content_id"],
                title=r["title"],
                source_name=r["source_name"],
                source_url=r["source_url"],
                published_at=datetime.fromisoformat(r["published_at"]),
            )
            for r in rows
        ]
