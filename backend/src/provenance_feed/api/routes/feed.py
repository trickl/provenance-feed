from __future__ import annotations

from fastapi import APIRouter, Depends

from provenance_feed.api.deps import get_repo
from provenance_feed.api.schemas import FeedItemOut
from provenance_feed.persistence.repository import FeedRepository

router = APIRouter(prefix="/api", tags=["feed"])


@router.get("/feed", response_model=list[FeedItemOut])
def list_feed(
    limit: int = 50,
    repo: FeedRepository = Depends(get_repo),
) -> list[FeedItemOut]:
    items = repo.list_latest(limit=limit)
    return [FeedItemOut.model_validate(i.model_dump()) for i in items]
