from __future__ import annotations

import logging

from provenance_feed.ingestion.rss_common import flatten
from provenance_feed.ingestion.rss_sources import (
    bbc,
    brookings,
    eff,
    guardian,
    nasa,
    npr,
    reliefweb,
)

logger = logging.getLogger(__name__)


def fetch_all_records(*, timeout_seconds: float = 10.0) -> list[dict]:
    """Fetch and parse all curated sources.

    Coverage is intentionally incomplete: we ingest a small, curated set of sources.
    """

    batches = [
        bbc.ingest(timeout_seconds=timeout_seconds),
        npr.ingest(timeout_seconds=timeout_seconds),
        guardian.ingest(timeout_seconds=timeout_seconds),
        nasa.ingest(timeout_seconds=timeout_seconds),
        # Legitimate but thinner/indirect sourcing (included to surface messiness; not endorsement).
        brookings.ingest(timeout_seconds=timeout_seconds),
        eff.ingest(timeout_seconds=timeout_seconds),
        reliefweb.ingest(timeout_seconds=timeout_seconds),
    ]
    records = flatten(batches)
    logger.info("ingestion fetched total=%s records", len(records))
    return records
