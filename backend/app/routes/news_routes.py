from fastapi import APIRouter, HTTPException, Query

from backend.app.services.search_service import search_news

router = APIRouter()


@router.get("/news/search", summary="Search for news articles based on a query")
def get_news(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=5, ge=1, le=20, description="Max number of results"),
):
    try:
        results = search_news(q, limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"query": q, "results": results}
