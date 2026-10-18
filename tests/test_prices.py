from pipeline.transformations.prices import filter_invalid_prices, transform_prices
import pandas as pd


def test_filter_invalid_prices_removes_invalid_rows():
    # Arrange: create sample market data
    df = pd.DataFrame(
        {
            "symbol": ["BTC-USD", "ETH-USD"],
            "open": [100, 100],
            "high": [120, 90],
            "low": [90, 80],
            "close": [110, 85],
            "volume": [1000, 2000],
        }
    )

    # Act: run the function
    result = filter_invalid_prices(df)

    # Assert: only the valid row should remain
    assert len(result) == 1
    assert result.iloc[0]["symbol"] == "BTC-USD"


def test_transform_prices_cleans_and_normalizes_data():
    raw_data = pd.DataFrame(
        {
            "Date": [
                "2026-10-15 10:00:00",
                "2026-10-15 10:00:00",
                "2026-10-15 11:00:00",
            ],
            "Open": [100, 100, 100],
            "High": [120, 120, 90],
            "Low": [90, 90, 80],
            "Close": [110, 110, 85],
            "Volume": [1000, 1000, 2000],
            "symbol": ["BTC-USD", "BTC-USD", "ETH-USD"],
        }
    )

    result = transform_prices(raw_data)
    print(result)
    # Duplicate BTC record is removed.
    # Invalid ETH record is removed.
    assert len(result) == 1

    # Column names are normalized.
    assert list(result.columns) == [
        "timestamp",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    # Timestamp and price data have the expected types.
    assert str(result["timestamp"].dtype) in {
        "datetime64[s, UTC]",
        "datetime64[us, UTC]",
        "datetime64[ns, UTC]",
    }
    assert result["close"].dtype.kind == "f"


def test_transform_prices_removes_rows_with_missing_values():
    raw_data = pd.DataFrame(
        {
            "Date": [
                "2026-10-15 10:00:00",
                "2026-10-15 11:00:00",
            ],
            "Open": [100, 100],
            "High": [120, 120],
            "Low": [90, 90],
            "Close": [110, None],
            "Volume": [1000, 2000],
            "symbol": ["BTC-USD", "ETH-USD"],
        }
    )

    result = transform_prices(raw_data)

    assert len(result) == 1
    assert result.iloc[0]["symbol"] == "BTC-USD"
    assert result.isna().sum().sum() == 0


def test_transform_prices_handles_empty_dataframe():
    raw_data = pd.DataFrame()

    result = transform_prices(raw_data)

    assert result.empty
    assert list(result.columns) == []
