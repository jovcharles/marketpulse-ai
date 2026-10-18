import pandas as pd

from loaders.postgres import get_connection


def load_prices(prices: pd.DataFrame) -> int:
    """Insert or update cryptocurrency prices in PostgreSQL."""
    if prices.empty:
        print("No prices to load.")
        return 0

    query = """
        INSERT INTO prices (
            symbol, timestamp, open, high, low, close, volume
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol, timestamp)
        DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume;
    """

    columns = [
        "symbol",
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    rows = list(prices[columns].itertuples(index=False, name=None))

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, rows)

    return len(rows)
