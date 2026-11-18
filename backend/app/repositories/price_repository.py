from datetime import date, datetime
from typing import Any

from shared.database.connection import get_connection
from backend.app.services.sql_validator import validate_read_only_sql


class PriceRepository:
    """Repository for structured, read-only cryptocurrency price queries."""

    def __init__(self, connection_factory=get_connection, statement_timeout_ms: int = 5000):
        self._get_connection = connection_factory
        self.statement_timeout_ms = statement_timeout_ms

    def _execute_query(self, sql: str, params: list[Any] | tuple[Any, ...]) -> list[tuple]:
        """Validates and executes a read-only query with timeout enforcement."""
        validated_sql = validate_read_only_sql(sql)

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                # Set execution timeout on the transaction/connection
                cursor.execute(f"SET LOCAL statement_timeout = {int(self.statement_timeout_ms)};")
                cursor.execute(validated_sql, params)
                return cursor.fetchall()

    def get_prices(
        self,
        symbol: str,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
        limit: int = 1000,
        order_asc: bool = True,
    ) -> list[dict]:
        """Fetch historical OHLCV records for a given cryptocurrency symbol."""
        if not symbol:
            raise ValueError("Symbol must be specified.")

        limit = max(1, min(limit, 5000))
        conditions = ["symbol = %s"]
        params: list[Any] = [symbol]

        if start_date is not None:
            conditions.append("timestamp >= %s")
            params.append(start_date)

        if end_date is not None:
            conditions.append("timestamp <= %s")
            params.append(end_date)

        where_clause = " AND ".join(conditions)
        order_direction = "ASC" if order_asc else "DESC"

        sql = f"""
            SELECT
                symbol,
                timestamp,
                open,
                high,
                low,
                close,
                volume
            FROM prices
            WHERE {where_clause}
            ORDER BY timestamp {order_direction}
            LIMIT %s;
        """
        params.append(limit)

        rows = self._execute_query(sql, params)
        return [
            {
                "symbol": r[0],
                "timestamp": r[1],
                "open": float(r[2]),
                "high": float(r[3]),
                "low": float(r[4]),
                "close": float(r[5]),
                "volume": float(r[6]),
            }
            for r in rows
        ]

    def get_latest_price(self, symbol: str) -> dict | None:
        """Fetch the most recent price record for a cryptocurrency symbol."""
        if not symbol:
            raise ValueError("Symbol must be specified.")

        sql = """
            SELECT
                symbol,
                timestamp,
                open,
                high,
                low,
                close,
                volume
            FROM prices
            WHERE symbol = %s
            ORDER BY timestamp DESC
            LIMIT 1;
        """
        rows = self._execute_query(sql, [symbol])
        if not rows:
            return None

        r = rows[0]
        return {
            "symbol": r[0],
            "timestamp": r[1],
            "open": float(r[2]),
            "high": float(r[3]),
            "low": float(r[4]),
            "close": float(r[5]),
            "volume": float(r[6]),
        }

    def get_price_summary(
        self,
        symbol: str,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
    ) -> dict | None:
        """Calculate aggregated price metrics (open, close, min, max, volume) over a date range."""
        if not symbol:
            raise ValueError("Symbol must be specified.")

        conditions = ["symbol = %s"]
        params: list[Any] = [symbol]

        if start_date is not None:
            conditions.append("timestamp >= %s")
            params.append(start_date)

        if end_date is not None:
            conditions.append("timestamp <= %s")
            params.append(end_date)

        where_clause = " AND ".join(conditions)

        sql = f"""
            WITH windowed AS (
                SELECT
                    timestamp,
                    open,
                    close,
                    low,
                    high,
                    volume,
                    FIRST_VALUE(open) OVER (ORDER BY timestamp ASC) AS first_open,
                    LAST_VALUE(close) OVER (
                        ORDER BY timestamp ASC
                        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                    ) AS last_close
                FROM prices
                WHERE {where_clause}
            )
            SELECT
                first_open,
                last_close,
                MIN(low) AS min_low,
                MAX(high) AS max_high,
                COALESCE(SUM(volume), 0) AS total_volume,
                COUNT(*) AS record_count
            FROM windowed
            GROUP BY first_open, last_close;
        """

        rows = self._execute_query(sql, params)
        if not rows or rows[0][5] == 0:
            return None

        r = rows[0]
        return {
            "symbol": symbol,
            "first_open": float(r[0]) if r[0] is not None else None,
            "last_close": float(r[1]) if r[1] is not None else None,
            "min_low": float(r[2]) if r[2] is not None else None,
            "max_high": float(r[3]) if r[3] is not None else None,
            "total_volume": float(r[4]) if r[4] is not None else 0.0,
            "record_count": int(r[5]),
        }

    def get_moving_average(
        self,
        symbol: str,
        window: int = 7,
        limit: int = 100,
    ) -> list[dict]:
        """Compute rolling simple moving average using SQL window functions."""
        if not symbol:
            raise ValueError("Symbol must be specified.")

        if window < 1 or window > 365:
            raise ValueError("Window must be between 1 and 365.")

        limit = max(1, min(limit, 1000))
        preceding = window - 1

        sql = f"""
            WITH ma_data AS (
                SELECT
                    timestamp,
                    close,
                    AVG(close) OVER (
                        ORDER BY timestamp ASC
                        ROWS BETWEEN {preceding} PRECEDING AND CURRENT ROW
                    ) AS moving_avg
                FROM prices
                WHERE symbol = %s
            )
            SELECT timestamp, close, moving_avg
            FROM ma_data
            ORDER BY timestamp DESC
            LIMIT %s;
        """

        rows = self._execute_query(sql, [symbol, limit])
        return [
            {
                "timestamp": r[0],
                "close": float(r[1]),
                "moving_average": round(float(r[2]), 6),
            }
            for r in rows
        ]

    def get_available_symbols(self) -> list[str]:
        """Return all distinct cryptocurrency symbols available in the database."""
        sql = "SELECT DISTINCT symbol FROM prices ORDER BY symbol ASC;"
        rows = self._execute_query(sql, [])
        return [r[0] for r in rows]


price_repository = PriceRepository()
