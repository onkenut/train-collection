from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas import SearchResponse, SearchResult
from ..services.search_service import search_pages, count_search_results

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1),
    notebook_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    tag: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    total = await count_search_results(db, q, notebook_id, date_from, date_to, tag)
    results = await search_pages(db, q, notebook_id, date_from, date_to, tag, limit, offset)
    return SearchResponse(
        results=[SearchResult(**r) for r in results],
        total=total,
    )
