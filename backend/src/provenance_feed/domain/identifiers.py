from __future__ import annotations


def make_content_id(*, source: str, source_item_id: str) -> str:
    """Create a stable, opaque identifier for content.

    This identifier is designed to be stable across re-ingestion, and later can be
    used to query an external provenance/trust system.
    """

    source_norm = source.strip().lower()
    source_item_norm = source_item_id.strip()
    if not source_norm or not source_item_norm:
        raise ValueError("source and source_item_id must be non-empty")
    return f"{source_norm}:{source_item_norm}"
