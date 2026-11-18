from datetime import date, datetime, timezone
from unittest.mock import patch
import pytest
from fastapi import HTTPException

from backend.app.routes.price_routes import (
    compare_market,
    execute_query_plan,
    get_latest_price,
    get_moving_average,
    get_price_history,
    get_price_summary,
)
from backend.app.schemas.prices import MarketComparisonRequest
from backend.app.schemas.query_plan import QueryPlan


def test_route_get_latest_price():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    mock_record = {
        "symbol": "BTC-USD",
        "timestamp": now,
        "open": 60000.0,
        "high": 61000.0,
        "low": 59000.0,
        "close": 60500.0,
        "volume": 120.0,
    }
    with patch("backend.app.routes.price_routes.price_service.get_latest_price", return_value=mock_record):
        res = get_latest_price(symbol="BTC-USD")
        assert res.symbol == "BTC-USD"
        assert res.close == 60500.0


def test_route_get_price_history_validates_dates():
    with pytest.raises(HTTPException) as exc_info:
        get_price_history(
            symbol="BTC-USD",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 1, 1),
        )
    assert exc_info.value.status_code == 400
    assert "cannot be earlier than start date" in exc_info.value.detail


def test_route_get_price_summary():
    mock_summary = {
        "symbol": "BTC-USD",
        "start_date": "2026-01-01",
        "end_date": "2026-01-31",
        "first_open": 50000.0,
        "last_close": 55000.0,
        "min_low": 48000.0,
        "max_high": 56000.0,
        "total_volume": 10000.0,
        "price_change": 5000.0,
        "percentage_change": 10.0,
        "record_count": 31,
    }
    with patch("backend.app.routes.price_routes.price_service.get_price_summary", return_value=mock_summary):
        res = get_price_summary(symbol="BTC-USD", start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
        assert res.symbol == "BTC-USD"
        assert res.price_change == 5000.0


def test_route_get_moving_average():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    mock_ma = {
        "symbol": "BTC-USD",
        "window": 7,
        "count": 1,
        "records": [{"timestamp": now, "close": 50000.0, "moving_average": 49500.0}],
    }
    with patch("backend.app.routes.price_routes.price_service.get_moving_average", return_value=mock_ma):
        res = get_moving_average(symbol="BTC-USD", window=7, limit=10)
        assert res.window == 7
        assert len(res.records) == 1
        assert res.records[0].moving_average == 49500.0


def test_route_compare_market():
    mock_comparison = {
        "comparisons": [
            {
                "symbol": "BTC-USD",
                "first_price": 50000.0,
                "latest_price": 60000.0,
                "price_change": 10000.0,
                "percentage_change": 20.0,
                "period_high": 61000.0,
                "period_low": 49000.0,
                "total_volume": 500.0,
                "record_count": 10,
            }
        ],
        "start_date": None,
        "end_date": None,
    }
    with patch("backend.app.routes.price_routes.price_service.compare_market", return_value=mock_comparison):
        req = MarketComparisonRequest(symbols=["BTC-USD"])
        res = compare_market(req)
        assert len(res.comparisons) == 1
        assert res.comparisons[0].symbol == "BTC-USD"


def test_route_execute_query_plan():
    plan = QueryPlan(
        original_question="What is the price of Bitcoin?",
        intent="market_lookup",
        asset_symbols=["BTC-USD"],
        retrieval_sources=["sql"],
    )
    with patch("backend.app.routes.price_routes.price_service.execute_query_plan", return_value={"status": "success"}):
        res = execute_query_plan(plan)
        assert res["status"] == "success"
