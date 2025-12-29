from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from provenance_feed.ingestion.rss_common import RSSSource, parse_rss_xml


def _fixture(path: str) -> bytes:
    p = Path(__file__).parent / "fixtures" / path
    return p.read_bytes()


def test_rss_missing_timestamp_is_skipped() -> None:
    source = RSSSource(source_id="test", source_name="Test", feed_url="https://example.invalid")

    # Minimal RSS 2.0 without a pubDate.
    xml = b"""<?xml version='1.0' encoding='UTF-8'?>
    <rss version='2.0'>
      <channel>
        <title>Test</title>
        <item>
          <title>Hello</title>
          <link>https://example.com/a</link>
        </item>
      </channel>
    </rss>
    """

    records = parse_rss_xml(xml=xml, source=source, page_fetcher=None)
    assert records == []


def test_rss_duplicate_url_dedup_keeps_one() -> None:
    source = RSSSource(source_id="test", source_name="Test", feed_url="https://example.invalid")

    xml = b"""<?xml version='1.0' encoding='UTF-8'?>
    <rss version='2.0'>
      <channel>
        <title>Test</title>
        <item>
          <title>First title</title>
          <link>https://example.com/a?utm_source=x</link>
          <pubDate>Mon, 01 Jan 2024 10:00:00 GMT</pubDate>
        </item>
        <item>
          <title>Updated title</title>
          <link>https://example.com/a</link>
          <pubDate>Mon, 01 Jan 2024 10:05:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    # Avoid network: provide a stub fetcher that returns a no-image page.
    def fetcher(_url: str, _timeout: float) -> bytes:
        return _fixture("html_no_image.html")

    records = parse_rss_xml(
        xml=xml,
        source=source,
        page_fetcher=fetcher,
        now=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
    )
    assert len(records) == 1
    assert records[0]["source"] == "test"
    assert records[0]["source_url"] == "https://example.com/a"
    assert records[0]["title"] == "Updated title"


def test_rss_image_extraction_from_media_content() -> None:
    source = RSSSource(source_id="test", source_name="Test", feed_url="https://example.invalid")

    records = parse_rss_xml(
        xml=_fixture("rss_with_media.xml"),
        source=source,
        page_fetcher=None,
        now=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
    )
    assert len(records) == 1
    assert records[0]["image_url"] == "https://cdn.example.com/image.jpg"
    assert records[0]["image_source"] == "rss"


def test_og_image_fallback_when_no_rss_image() -> None:
    source = RSSSource(source_id="test", source_name="Test", feed_url="https://example.invalid")

    def fetcher(_url: str, _timeout: float) -> bytes:
        return _fixture("html_with_og_image.html")

    records = parse_rss_xml(
        xml=_fixture("rss_no_media.xml"),
        source=source,
        page_fetcher=fetcher,
        now=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
    )
    assert len(records) == 1
    assert records[0]["image_url"] == "https://images.example.com/og.jpg"
    assert records[0]["image_source"] == "page_meta"


def test_no_image_sets_none_source() -> None:
    source = RSSSource(source_id="test", source_name="Test", feed_url="https://example.invalid")

    def fetcher(_url: str, _timeout: float) -> bytes:
        return _fixture("html_no_image.html")

    records = parse_rss_xml(
        xml=_fixture("rss_no_media.xml"),
        source=source,
        page_fetcher=fetcher,
        now=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
    )
    assert len(records) == 1
    assert records[0]["image_url"] is None
    assert records[0]["image_source"] == "none"