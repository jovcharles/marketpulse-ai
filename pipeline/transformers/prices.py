"""
Build the transformer
In transformers/prices.py, accept the raw records and return cleaned data.
Use Pandas for tasks such as:
- Converting timestamps to a consistent timezone.
- Ensuring prices and volume are numeric.
- Detecting missing or invalid values.
- Checking that prices are positive and that high/low values make sense.
- Removing duplicates within the incoming batch.
"""

import pandas as pd


def transform_prices(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate raw cryptocurrency price data"""
    if raw_data.empty:
        print("Data is empty")
        return pd.DataFrame()
    columns = {
        "Date": "timestamp",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Volume": "volume",
        "Close": "close",
    }

    raw_data = raw_data.rename(columns=columns)

    raw_data["timestamp"] = pd.to_datetime(
        raw_data["timestamp"], utc=True, errors="coerce"
    )
    raw_data = raw_data[
        ["timestamp", "symbol", "open", "high", "low", "close", "volume"]
    ]

    numeric_columns = ["open", "high", "low", "close", "volume"]

    for column in numeric_columns:
        raw_data[column] = pd.to_numeric(
            raw_data[column],
            errors="coerce",
        ).astype(float)

    raw_data = raw_data.drop_duplicates(subset=["symbol", "timestamp"], keep="last")
    raw_data = raw_data.dropna()
    raw_data = filter_invalid_prices(raw_data)
    return raw_data


def filter_invalid_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out rows with invalid price data"""
    df = df[(df["open"] >= 0) & (df["close"] >= 0)]
    # Filter out rows where the high price is less than the low price
    df = df[df["high"] >= df["low"]]

    # Filter out rows where the high price is less than the open or close price
    df = df[(df["high"] >= df["open"]) & (df["high"] >= df["close"])]
    # Filter out rows where the low price is greater than the open or close price
    df = df[(df["low"] <= df["open"]) & (df["low"] <= df["close"])]
    # Volume cannot be negative
    df = df[df["volume"] >= 0]

    return df
