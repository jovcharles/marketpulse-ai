from pipeline.transformers.prices import filter_invalid_prices
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
