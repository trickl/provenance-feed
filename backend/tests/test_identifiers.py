import pytest

from provenance_feed.domain.identifiers import make_content_id


def test_make_content_id_is_stable_and_normalised() -> None:
    assert make_content_id(source="Mock", source_item_id="123") == "mock:123"


def test_make_content_id_rejects_empty() -> None:
    with pytest.raises(ValueError):
        make_content_id(source="", source_item_id="1")
    with pytest.raises(ValueError):
        make_content_id(source="mock", source_item_id="")
