from datetime import date, datetime, timezone
from unittest.mock import MagicMock
import pytest

from backend.app.schemas.query_plan import DateRange, QueryPlan
from backend.app.services.prices_services import PriceService


@pytest.fixture
def mock_repo():
    return MagicMock()


def test_service_latest_price(mock_repo):
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    mock_repo.get_latest_price.return_value = {
        "symbol": "BTC-USD",
        "timestamp": now,
        "open": 60000.0,
        "high": 61000.0,
        "low": 59000.0,
        "close": 60500.0,
        "volume": 250.0,
    }

    service = PriceService(repository=mock_repo)
    result = service.get_latest_price("btc-usd")

    mock_repo.get_latest_price.assert_called_once_with("BTC-USD")
    assert result["symbol"] == "BTC-USD"
    assert result["close"] == 60500.0


def test_service_price_summary_calculates_returns(mock_repo):
    mock_repo.get_price_summary.return_value = {
        "symbol": "BTC-USD",
        "first_open": 50000.0,
        "last_close": 55000.0,
        "min_low": 48000.0,
        "max_high": 56000.0,
        "total_volume": 10000.0,
        "record_count": 10,
    }

    service = PriceService(repository=mock_repo)
    summary = service.get_price_summary("BTC-USD")

    assert summary["price_change"] == 5000.0
    assert summary["percentage_change"] == 10.0
    assert summary["record_count"] == 10


def test_service_price_summary_handles_empty(mock_repo):
    mock_repo.get_price_summary.return_value = None

    service = PriceService(repository=mock_repo)
    summary = service.get_price_summary("UNKNOWN-USD")

    assert summary["record_count"] == 0
    assert summary["price_change"] is None
    assert summary["percentage_change"] is None


def test_service_compare_market(mock_repo):
    mock_repo.get_price_summary.side_effect = [
        {
            "symbol": "BTC-USD",
            "first_open": 50000.0,
            "last_close": 60000.0,
            "min_low": 49000.0,
            "max_high": 61000.0,
            "total_volume": 5000.0,
            "record_count": 5,
        },
        {
            "symbol": "ETH-USD",
            "first_open": 2000.0,
            "last_close": 1800.0,
            "min_low": 1700.0,
            "max_high": 2100.0,
            "total_volume": 12000.0,
            "record_count": 5,
        },
    ]

    service = PriceService(repository=mock_repo)
    result = service.compare_market(["BTC-USD", "ETH-USD"])

    assert len(result["comparisons"]) == 2
    btc = result["comparisons"][0]
    eth = result["comparisons"][1]

    assert btc["percentage_change"] == 20.0
    assert eth["percentage_change"] == -10.0


def test_service_execute_query_plan_lookup(mock_repo):
    mock_repo.get_latest_price.return_value = {
        "symbol": "BTC-USD",
        "close": 65000.0,
    }

    service = PriceService(repository=mock_repo)
    plan = QueryPlan(
        original_question="What is the price of Bitcoin?",
        intent="market_lookup",
        asset_symbols=["BTC-USD"],
        retrieval_sources=["sql"],
    )

    result = service.execute_query_plan(plan)
    assert result["status"] == "success"
    assert result["retrieval_type"] == "sql"
    assert result["data"]["latest_price"]["close"] == 65000.0


def test_service_execute_query_plan_comparison(mock_repo):
    mock_repo.get_price_summary.return_value = {
        "symbol": "BTC-USD",
        "first_open": 50000.0,
        "last_close": 55000.0,
        "min_low": 48000.0,
        "max_high": 56000.0,
        "total_volume": 10000.0,
        "record_count": 10,
    }

    service = PriceService(repository=mock_repo)
    plan = QueryPlan(
        original_question="Compare Bitcoin and Ethereum last month",
        intent="market_comparison",
        asset_symbols=["BTC-USD", "ETH-USD"],
        date_range=DateRange(start=date(2026, 1, 1), end=date(2026, 1, 31)),
        retrieval_sources=["sql"],
    )

    result = service.execute_query_plan(plan)
    assert result["status"] == "success"
    assert result["retrieval_type"] == "sql"
    assert "comparisons" in result["data"]


def test_service_execute_query_plan_skips_non_sql():
    service = PriceService(repository=MagicMock())
    plan = QueryPlan(
        original_question="What is the latest news?",
        intent="news_search",
        asset_symbols=[],
        retrieval_sources=["vector"],
        semantic_query="latest news",
    )
    result = service.execute_query_plan(plan)
    assert result["status"] == "skipped"
