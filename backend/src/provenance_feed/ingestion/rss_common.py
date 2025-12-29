from __future__ import annotations

import hashlib
import html.parser
import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import feedparser

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RSSSource:
    source_id: str
    source_name: str
    feed_url: str


TRACKING_QUERY_PREFIXES = ("utm_",)

TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "igshid",
    "ref",
}


def canonicalise_url(url: str) -> str:
    """Best-effort URL canonicalisation.

    Intended for stable identification and de-duplication.

    This is deliberately conservative and minimal; real URL canonicalisation is messy.
    TODO: consider per-source canonicalisation rules when real data exposes problems.
    """

    url = url.strip()
    parts = urlsplit(url)

    scheme = (parts.scheme or "https").lower()
    netloc = parts.netloc.lower()

    # Drop fragments.
    fragment = ""

    # Remove common tracking params.
    kept_qs: list[tuple[str, str]] = []
    for k, v in parse_qsl(parts.query, keep_blank_values=True):
        kl = k.lower()
        if kl in TRACKING_QUERY_KEYS:
            continue
        if any(kl.startswith(p) for p in TRACKING_QUERY_PREFIXES):
            continue
        kept_qs.append((k, v))
    query = urlencode(kept_qs, doseq=True)

    return urlunsplit((scheme, netloc, parts.path, query, fragment))


def source_item_id_from_canonical_url(canonical_url: str) -> str:
    """Derive a stable-ish source item id from a canonical URL.

    Many real feeds have missing/unstable GUIDs. We prefer a URL-hash-based id for
    resilience and explicit de-duplication.

    TODO: this can fail if canonical URLs change over time, or if multiple distinct
    stories share the same canonical URL.
    """

    digest = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()
    return digest


def _best_effort_published_at(entry: feedparser.FeedParserDict) -> datetime | None:
    # feedparser provides published_parsed/updated_parsed as time.struct_time.
    ts = entry.get("published_parsed") or entry.get("updated_parsed")
    if not ts:
        return None
    # struct_time -> datetime
    return datetime(*ts[:6], tzinfo=UTC)


def fetch_feed_xml(*, url: str, timeout_seconds: float = 10.0) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "provenance-feed/0.1 (https://github.com/trickl/provenance-feed)",
            "Accept": (
                "application/rss+xml, application/atom+xml, application/xml, "
                "text/xml;q=0.9, */*;q=0.1"
            ),
        },
        method="GET",
    )
    with urlopen(req, timeout=timeout_seconds) as resp:
        return resp.read()


def fetch_page_html(*, url: str, timeout_seconds: float = 10.0) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "provenance-feed/0.1 (https://github.com/trickl/provenance-feed)",
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1",
        },
        method="GET",
    )
    with urlopen(req, timeout=timeout_seconds) as resp:
        return resp.read()


def _is_http_url(url: str | None) -> bool:
    if not url:
        return False
    u = url.strip().lower()
    return u.startswith("http://") or u.startswith("https://")


def extract_image_from_rss_entry(entry: feedparser.FeedParserDict) -> str | None:
    """Best-effort extraction of an image URL from RSS/Atom entry data."""

    for key in ("media_content", "media_thumbnail"):
        media = entry.get(key) or []
        if isinstance(media, dict):
            media = [media]
        for m in media:
            if not isinstance(m, dict):
                continue
            url = m.get("url")
            if _is_http_url(url):
                return str(url)

    links = entry.get("links") or []
    for link in links:
        if not isinstance(link, dict):
            continue
        if (link.get("rel") or "").lower() != "enclosure":
            continue
        t = (link.get("type") or "").lower()
        href = link.get("href")
        if t.startswith("image/") and _is_http_url(href):
            return str(href)

    img = entry.get("image")
    if isinstance(img, dict):
        url = img.get("href") or img.get("url")
        if _is_http_url(url):
            return str(url)

    return None


class _MetaImageParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.og_image: str | None = None
        self.twitter_image: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "meta":
            return

        a = {k.lower(): (v or "") for k, v in attrs}
        key = (a.get("property") or a.get("name") or "").lower()
        content = (a.get("content") or "").strip()
        if not content:
            return

        if key == "og:image" and self.og_image is None:
            self.og_image = content
        elif key == "twitter:image" and self.twitter_image is None:
            self.twitter_image = content


def extract_image_from_html_meta(*, html_bytes: bytes, base_url: str) -> str | None:
    """Extract og:image / twitter:image from HTML.

    Parses only the <meta> tags required for image discovery.
    """

    try:
        text = html_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return None

    parser = _MetaImageParser()
    try:
        parser.feed(text)
    except Exception:
        return None

    candidate = parser.og_image or parser.twitter_image
    if not candidate:
        return None

    resolved = urljoin(base_url, candidate)
    return resolved if _is_http_url(resolved) else None


def resolve_image_for_entry(
    *,
    entry: feedparser.FeedParserDict,
    canonical_url: str,
    now: datetime,
    timeout_seconds: float,
    page_fetcher: Callable[[str, float], bytes] | None,
) -> tuple[str | None, str, str]:
    """Resolve image using RSS first, then page metadata.

    Returns (image_url, image_source, image_last_checked_iso).
    """

    checked = now.astimezone(UTC).isoformat()

    rss_url = extract_image_from_rss_entry(entry)
    if rss_url:
        return rss_url, "rss", checked

    if page_fetcher is None:
        return None, "none", checked

    try:
        html_bytes = page_fetcher(canonical_url, timeout_seconds)
        meta_url = extract_image_from_html_meta(html_bytes=html_bytes, base_url=canonical_url)
        if meta_url:
            return meta_url, "page_meta", checked
    except Exception as e:
        # Fail quietly; page fetch is best-effort and not critical to core ingestion.
        logger.debug("page meta fetch failed (url=%s): %s", canonical_url, type(e).__name__)

    return None, "none", checked


def parse_rss_xml(
    *,
    xml: bytes,
    source: RSSSource,
    timeout_seconds: float = 10.0,
    page_fetcher: Callable[[str, float], bytes] | None = fetch_page_html,
    now: datetime | None = None,
) -> list[dict]:
    """Parse an RSS/Atom payload and return normalisation-ready raw records.

    Returns dicts compatible with `normalise_record()`.
    """

    parsed = feedparser.parse(xml)

    if parsed.bozo:
        # bozo_exception is helpful but can contain huge reprs; log the type.
        ex = getattr(parsed, "bozo_exception", None)
        logger.warning(
            "RSS parse bozo=%s for source=%s (%s): %s",
            parsed.bozo,
            source.source_id,
            source.feed_url,
            type(ex).__name__ if ex else "unknown",
        )

    raw_by_content_id: dict[str, dict] = {}
    skipped = 0

    for entry in parsed.entries or []:
        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()

        if not title:
            skipped += 1
            logger.info("skip item: missing title (source=%s)", source.source_id)
            continue
        if not link:
            skipped += 1
            logger.info("skip item: missing link (source=%s)", source.source_id)
            continue

        published_at = _best_effort_published_at(entry)
        if not published_at:
            skipped += 1
            logger.info("skip item: missing timestamp (source=%s url=%s)", source.source_id, link)
            continue

        canonical_url = canonicalise_url(link)
        source_item_id = source_item_id_from_canonical_url(canonical_url)
        content_id = f"{source.source_id}:{source_item_id}"

        n = now or datetime.now(tz=UTC)
        image_url, image_source, image_last_checked = resolve_image_for_entry(
            entry=entry,
            canonical_url=canonical_url,
            now=n,
            timeout_seconds=timeout_seconds,
            page_fetcher=page_fetcher,
        )

        record = {
            "source": source.source_id,
            "source_item_id": source_item_id,
            "title": title,
            "source_name": source.source_name,
            "source_url": canonical_url,
            "published_at": published_at.isoformat(),
            "image_url": image_url,
            "image_source": image_source,
            "image_last_checked": image_last_checked,
        }

        # Duplicate handling: keep the most recent timestamp for the same content_id.
        existing = raw_by_content_id.get(content_id)
        if existing is None:
            raw_by_content_id[content_id] = record
        else:
            try:
                existing_dt = datetime.fromisoformat(existing["published_at"]).astimezone(UTC)
                new_dt = datetime.fromisoformat(record["published_at"]).astimezone(UTC)
            except Exception:
                # If parsing fails, prefer the latest seen record.
                raw_by_content_id[content_id] = record
            else:
                if new_dt >= existing_dt:
                    raw_by_content_id[content_id] = record

    logger.info(
        "parsed source=%s entries=%s kept=%s skipped=%s",
        source.source_id,
        len(parsed.entries or []),
        len(raw_by_content_id),
        skipped,
    )

    return list(raw_by_content_id.values())


def ingest_source(*, source: RSSSource, timeout_seconds: float = 10.0) -> list[dict]:
    """Fetch and parse one RSS source into raw normalisation records."""

    xml = fetch_feed_xml(url=source.feed_url, timeout_seconds=timeout_seconds)
    return parse_rss_xml(xml=xml, source=source, timeout_seconds=timeout_seconds)


def flatten(records: Iterable[list[dict]]) -> list[dict]:
    out: list[dict] = []
    for batch in records:
        out.extend(batch)
    return out
