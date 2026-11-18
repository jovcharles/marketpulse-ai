from datetime import date, timedelta
import pytest
from backend.app.schemas.query_plan import DateRange, QueryPlan
from backend.app.services.query_planner.deterministic import (
    extract_assets,
    extract_date_range,
    parse_deterministic_plan,
)
from backend.app.services.query_planner.llm_provider import MockLLMProvider
from backend.app.services.query_planner.service import QueryPlannerService


REF_DATE = date(2026, 11, 18)


# ---------------------------------------------------------
# Asset Extraction Tests
# ---------------------------------------------------------


def test_extract_assets_single_common_names():
    assert extract_assets("What is the price of Bitcoin?") == ["BTC-USD"]
    assert extract_assets("Tell me about Ethereum") == ["ETH-USD"]
    assert extract_assets("How is solana doing?") == ["SOL-USD"]
    assert extract_assets("Check Ripple and Cardano") == ["XRP-USD", "ADA-USD"]


def test_extract_assets_tickers():
    assert extract_assets("What is the volume for BTC?") == ["BTC-USD"]
    assert extract_assets("Look up ETH-USD and SOL") == ["ETH-USD", "SOL-USD"]


def test_extract_assets_avoids_substring_false_positives():
    # 'eth' should not match 'method', 'sol' should not match 'solid'
    assert extract_assets("This method is solid and dependable.") == []


def test_extract_assets_multi_word_asset():
    assert extract_assets("What is the market cap of Binance Coin?") == ["BNB-USD"]


# ---------------------------------------------------------
# Date Range Extraction Tests
# ---------------------------------------------------------


def test_extract_date_range_relative():
    # Today: start=REF_DATE, end=REF_DATE + 1 day
    dr_today = extract_date_range("What is Bitcoin price today?", reference_date=REF_DATE)
    assert dr_today is not None
    assert dr_today.start == REF_DATE
    assert dr_today.end == REF_DATE + timedelta(days=1)

    # Yesterday: start=REF_DATE - 1 day, end=REF_DATE
    dr_yesterday = extract_date_range(
        "Why did ETH crash yesterday?", reference_date=REF_DATE
    )
    assert dr_yesterday is not None
    assert dr_yesterday.start == REF_DATE - timedelta(days=1)
    assert dr_yesterday.end == REF_DATE

    # Last 7 days / last week
    dr_week = extract_date_range(
        "Show BTC performance over the past week", reference_date=REF_DATE
    )
    assert dr_week is not None
    assert dr_week.start == REF_DATE - timedelta(days=7)
    assert dr_week.end == REF_DATE

    # Last 30 days / last month
    dr_month = extract_date_range(
        "Prices for SOL in the last month", reference_date=REF_DATE
    )
    assert dr_month is not None
    assert dr_month.start == REF_DATE - timedelta(days=30)
    assert dr_month.end == REF_DATE


def test_extract_date_range_explicit_iso():
    dr = extract_date_range("Price of BTC from 2026-10-01 to 2026-10-15")
    assert dr is not None
    assert dr.start == date(2026, 10, 1)
    assert dr.end == date(2026, 10, 15)


def test_extract_date_range_none_when_unspecified():
    dr = extract_date_range("What is Bitcoin?")
    assert dr is None


# ---------------------------------------------------------
# Intent Classification & Routing Tests (Deterministic)
# ---------------------------------------------------------


def test_market_lookup_intent():
    plan = parse_deterministic_plan(
        "What was the closing price of Bitcoin yesterday?", reference_date=REF_DATE
    )
    assert plan is not None
    assert plan.intent == "market_lookup"
    assert plan.asset_symbols == ["BTC-USD"]
    assert plan.retrieval_sources == ["sql"]
    assert plan.semantic_query is None
    assert plan.date_range is not None


def test_news_search_intent():
    plan = parse_deterministic_plan("Show me recent headlines and news about Ethereum")
    assert plan is not None
    assert plan.intent == "news_search"
    assert plan.asset_symbols == ["ETH-USD"]
    assert plan.retrieval_sources == ["vector"]
    assert plan.semantic_query is not None


def test_market_event_analysis_hybrid_intent():
    plan = parse_deterministic_plan(
        "Why did Bitcoin crash yesterday?", reference_date=REF_DATE
    )
    assert plan is not None
    assert plan.intent == "market_event_analysis"
    assert plan.asset_symbols == ["BTC-USD"]
    assert set(plan.retrieval_sources) == {"sql", "vector"}
    assert plan.semantic_query == "Why did Bitcoin crash yesterday?"
    assert plan.date_range is not None


def test_market_comparison_intent():
    plan = parse_deterministic_plan("Compare BTC and ETH volume over the last 7 days")
    assert plan is not None
    assert plan.intent == "market_comparison"
    assert set(plan.asset_symbols) == {"BTC-USD", "ETH-USD"}
    assert plan.retrieval_sources == ["sql"]


def test_general_question_intent():
    plan = parse_deterministic_plan("Hello! Who are you and what can you do?")
    assert plan is not None
    assert plan.intent == "general_question"
    assert plan.asset_symbols == []
    assert plan.retrieval_sources == []
    assert plan.semantic_query is None


# ---------------------------------------------------------
# Schema Validation Rule Tests
# ---------------------------------------------------------


def test_query_plan_validation_market_event_analysis_requires_both_sources():
    # Should fail if market_event_analysis does not have both sql and vector
    with pytest.raises(ValueError, match="Market event analysis requires SQL and vector retrieval"):
        QueryPlan(
            original_question="Why did BTC drop?",
            intent="market_event_analysis",
            asset_symbols=["BTC-USD"],
            retrieval_sources=["sql"],
            semantic_query="Why did BTC drop?",
        )


def test_query_plan_validation_vector_requires_semantic_query():
    # Should fail if vector source is requested without semantic_query
    with pytest.raises(ValueError, match="Semantic query is required for vector retrieval"):
        QueryPlan(
            original_question="Recent news",
            intent="news_search",
            asset_symbols=[],
            retrieval_sources=["vector"],
            semantic_query=None,
        )


def test_date_range_validation_end_must_be_after_start():
    with pytest.raises(ValueError, match="End date must be later than start date"):
        DateRange(start=date(2026, 11, 18), end=date(2026, 11, 18))

    with pytest.raises(ValueError, match="End date must be later than start date"):
        DateRange(start=date(2026, 11, 18), end=date(2026, 11, 10))


# ---------------------------------------------------------
# Planner Service & LLM Fallback Tests
# ---------------------------------------------------------


def test_planner_service_deterministic_fast_path():
    service = QueryPlannerService(llm_provider=None)
    plan = service.plan_query("What is the price of Solana?")
    assert plan.intent == "market_lookup"
    assert plan.asset_symbols == ["SOL-USD"]
    assert plan.retrieval_sources == ["sql"]


def test_planner_service_llm_fallback_for_ambiguous_query():
    mock_plan = {
        "intent": "news_search",
        "asset_symbols": ["BTC-USD"],
        "date_range": None,
        "retrieval_sources": ["vector"],
        "semantic_query": "whales accumulating crypto",
    }
    mock_provider = MockLLMProvider(mock_plan)
    service = QueryPlannerService(llm_provider=mock_provider)

    plan = service.plan_query("Are big players buying up coins right now?")
    assert plan.intent == "news_search"
    assert plan.asset_symbols == ["BTC-USD"]
    assert plan.retrieval_sources == ["vector"]
    assert plan.semantic_query == "whales accumulating crypto"


def test_planner_service_graceful_fallback_when_llm_fails():
    class FailingProvider(MockLLMProvider):
        def generate_plan(self, question: str):
            raise RuntimeError("Ollama service unreachable")

    service = QueryPlannerService(llm_provider=FailingProvider())
    # Should not raise exception, but return a safe plan
    plan = service.plan_query("Is there an obscure trend happening?")
    assert plan.intent == "general_question"
    assert plan.retrieval_sources == []


# ---------------------------------------------------------
# API Route Endpoint Tests
# ---------------------------------------------------------


def test_api_query_plan_endpoint():
    from backend.app.routes.query_routes import create_query_plan, QueryPlanRequest

    request = QueryPlanRequest(query="Why did Bitcoin crash yesterday?")
    plan = create_query_plan(request)

    assert plan.intent == "market_event_analysis"
    assert "BTC-USD" in plan.asset_symbols
    assert set(plan.retrieval_sources) == {"sql", "vector"}
    assert plan.semantic_query == "Why did Bitcoin crash yesterday?"


def test_api_query_plan_endpoint_empty_query():
    from pydantic import ValidationError
    from backend.app.routes.query_routes import QueryPlanRequest

    with pytest.raises(ValidationError):
        QueryPlanRequest(query="")
