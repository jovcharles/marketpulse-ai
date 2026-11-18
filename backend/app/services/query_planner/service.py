import logging
from datetime import date
from typing import Any

from pydantic import ValidationError

from backend.app.schemas.query_plan import DateRange, QueryPlan
from backend.app.services.query_planner.deterministic import (
    extract_assets,
    extract_date_range,
    parse_deterministic_plan,
)
from backend.app.services.query_planner.llm_provider import (
    BaseLLMProvider,
    get_llm_provider,
)

logger = logging.getLogger(__name__)


class QueryPlannerService:
    def __init__(self, llm_provider: BaseLLMProvider | None = None):
        self._llm_provider = llm_provider

    @property
    def llm_provider(self) -> BaseLLMProvider | None:
        if self._llm_provider is not None:
            return self._llm_provider
        return get_llm_provider()

    def plan_query(
        self, question: str, reference_date: date | None = None
    ) -> QueryPlan:
        """
        Produce a validated QueryPlan for the given natural language question.
        Uses deterministic pattern matching first; falls back to LLM for ambiguous queries.
        """
        cleaned = question.strip()
        if not cleaned:
            return QueryPlan(
                original_question=question,
                intent="general_question",
                asset_symbols=[],
                date_range=None,
                retrieval_sources=[],
                semantic_query=None,
            )

        # 1. Deterministic fast-path
        deterministic_plan = parse_deterministic_plan(
            cleaned, reference_date=reference_date
        )
        if deterministic_plan is not None:
            return deterministic_plan

        # 2. LLM Provider (if configured)
        provider = self.llm_provider
        if provider is not None:
            try:
                raw_plan = provider.generate_plan(cleaned)
                if raw_plan and isinstance(raw_plan, dict):
                    raw_plan["original_question"] = cleaned
                    # Handle date_range dictionary conversion if needed
                    dr_raw = raw_plan.get("date_range")
                    if isinstance(dr_raw, dict):
                        raw_plan["date_range"] = DateRange(**dr_raw)
                    return QueryPlan(**raw_plan)
            except (ValidationError, Exception) as e:
                logger.warning(
                    f"LLM planner output validation failed or error occurred: {e}. Falling back to default plan."
                )

        # 3. Graceful fallback for ambiguous queries
        assets = extract_assets(cleaned)
        date_range = extract_date_range(cleaned, reference_date=reference_date)

        if assets:
            return QueryPlan(
                original_question=cleaned,
                intent="market_lookup",
                asset_symbols=assets,
                date_range=date_range,
                retrieval_sources=["sql"],
                semantic_query=None,
            )

        return QueryPlan(
            original_question=cleaned,
            intent="general_question",
            asset_symbols=[],
            date_range=date_range,
            retrieval_sources=[],
            semantic_query=None,
        )


# Global singleton instance for easy import across backend
planner_service = QueryPlannerService()
