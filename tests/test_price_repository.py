from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest

from backend.app.repositories.price_repository import PriceRepository


@pytest.fixture
def mock_db():
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn_factory = MagicMock(return_value=mock_conn)
    mock_conn.__enter__.return_value = mock_conn
    return mock_conn_factory, mock_cursor


def test_get_prices_executes_parameterized_query(mock_db):
    conn_factory, mock_cursor = mock_db
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    mock_cursor.fetchall.return_value = [
        ("BTC-USD", now, 50000.0, 52000.0, 49000.0, 51500.0, 1000.0)
    ]

    repo = PriceRepository(connection_factory=conn_factory)
    prices = repo.get_prices("BTC-USD", limit=10)

    assert len(prices) == 1
    assert prices[0]["symbol"] == "BTC-USD"
    assert prices[0]["close"] == 51500.0
    assert mock_cursor.execute.call_count == 2
    # Verify timeout set
    assert "statement_timeout" in mock_cursor.execute.call_args_list[0][0][0]


def test_get_prices_requires_symbol(mock_db):
    conn_factory, _ = mock_db
    repo = PriceRepository(connection_factory=conn_factory)
    with pytest.raises(ValueError, match="Symbol must be specified"):
        repo.get_prices("")


def test_get_latest_price_returns_record_or_none(mock_db):
    conn_factory, mock_cursor = mock_db
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    mock_cursor.fetchall.return_value = [
        ("ETH-USD", now, 3000.0, 3100.0, 2900.0, 3050.0, 500.0)
    ]

    repo = PriceRepository(connection_factory=conn_factory)
    latest = repo.get_latest_price("ETH-USD")

    assert latest is not None
    assert latest["symbol"] == "ETH-USD"
    assert latest["open"] == 3000.0

    # Test None when no rows returned
    mock_cursor.fetchall.return_value = []
    assert repo.get_latest_price("UNKNOWN-USD") is None


def test_get_price_summary(mock_db):
    conn_factory, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        (40000.0, 45000.0, 39000.0, 46000.0, 150000.0, 24)
    ]

    repo = PriceRepository(connection_factory=conn_factory)
    summary = repo.get_price_summary("BTC-USD")

    assert summary is not None
    assert summary["symbol"] == "BTC-USD"
    assert summary["first_open"] == 40000.0
    assert summary["last_close"] == 45000.0
    assert summary["min_low"] == 39000.0
    assert summary["max_high"] == 46000.0
    assert summary["total_volume"] == 150000.0
    assert summary["record_count"] == 24


def test_get_moving_average_validates_window(mock_db):
    conn_factory, mock_cursor = mock_db
    repo = PriceRepository(connection_factory=conn_factory)

    with pytest.raises(ValueError, match="Window must be between 1 and 365"):
        repo.get_moving_average("BTC-USD", window=0)

    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    mock_cursor.fetchall.return_value = [(now, 50000.0, 49800.0)]
    records = repo.get_moving_average("BTC-USD", window=7)

    assert len(records) == 1
    assert records[0]["moving_average"] == 49800.0
