from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.schemas.query_plan import QueryPlan
from backend.app.services.query_planner.service import planner_service

router = APIRouter(prefix="/query", tags=["Query Planning"])


class QueryPlanRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Natural language question about cryptocurrency market or news",
        examples=["What was the price of Bitcoin last week?"],
    )


@router.post(
    "/plan",
    response_model=QueryPlan,
    summary="Generate an execution plan for a natural language query",
    description="Analyzes the query to identify intent, asset symbols, date ranges, and retrieval sources (SQL, Vector, or Hybrid).",
)
def create_query_plan(request: QueryPlanRequest) -> QueryPlan:
    try:
        plan = planner_service.plan_query(request.query)
        return plan
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate query plan: {str(e)}"
        )
