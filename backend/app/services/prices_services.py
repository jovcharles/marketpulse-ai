from datetime import date, datetime
from typing import Any

from backend.app.repositories.price_repository import PriceRepository, price_repository
from backend.app.schemas.query_plan import QueryPlan


class PriceService:
    """Service layer for cryptocurrency pricing business logic and analytics."""

    def __init__(self, repository: PriceRepository = price_repository):
        self.repository = repository

    def get_latest_price(self, symbol: str) -> dict[str, Any] | None:
        """Fetch the latest price for a symbol."""
        cleaned_symbol = symbol.strip().upper()
        return self.repository.get_latest_price(cleaned_symbol)

    def get_price_history(
        self,
        symbol: str,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
        limit: int = 1000,
    ) -> dict[str, Any]:
        """Fetch historical price series with record counts."""
        cleaned_symbol = symbol.strip().upper()
        prices = self.repository.get_prices(
            cleaned_symbol,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
        return {
            "symbol": cleaned_symbol,
            "count": len(prices),
            "prices": prices,
        }

    def get_price_summary(
        self,
        symbol: str,
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
    ) -> dict[str, Any]:
        """Compute summary statistics including absolute and percentage price change."""
        cleaned_symbol = symbol.strip().upper()
        summary = self.repository.get_price_summary(
            cleaned_symbol,
            start_date=start_date,
            end_date=end_date,
        )

        if not summary:
            return {
                "symbol": cleaned_symbol,
                "start_date": str(start_date) if start_date else None,
                "end_date": str(end_date) if end_date else None,
                "first_open": None,
                "last_close": None,
                "min_low": None,
                "max_high": None,
                "total_volume": 0.0,
                "price_change": None,
                "percentage_change": None,
                "record_count": 0,
            }

        first_open = summary.get("first_open")
        last_close = summary.get("last_close")

        price_change = None
        percentage_change = None

        if first_open is not None and last_close is not None:
            price_change = round(last_close - first_open, 6)
            if first_open != 0:
                percentage_change = round((price_change / first_open) * 100, 4)

        return {
            "symbol": cleaned_symbol,
            "start_date": str(start_date) if start_date else None,
            "end_date": str(end_date) if end_date else None,
            "first_open": first_open,
            "last_close": last_close,
            "min_low": summary.get("min_low"),
            "max_high": summary.get("max_high"),
            "total_volume": summary.get("total_volume", 0.0),
            "price_change": price_change,
            "percentage_change": percentage_change,
            "record_count": summary.get("record_count", 0),
        }

    def get_moving_average(
        self,
        symbol: str,
        window: int = 7,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Fetch rolling moving averages for a symbol."""
        cleaned_symbol = symbol.strip().upper()
        records = self.repository.get_moving_average(cleaned_symbol, window=window, limit=limit)
        return {
            "symbol": cleaned_symbol,
            "window": window,
            "count": len(records),
            "records": records,
        }

    def compare_market(
        self,
        symbols: list[str],
        start_date: date | datetime | str | None = None,
        end_date: date | datetime | str | None = None,
    ) -> dict[str, Any]:
        """Compare performance across multiple assets for an optional timeframe."""
        if not symbols:
            raise ValueError("At least one symbol must be provided for comparison.")

        results = []
        for sym in symbols:
            cleaned_sym = sym.strip().upper()
            summary = self.get_price_summary(cleaned_sym, start_date=start_date, end_date=end_date)
            results.append(
                {
                    "symbol": cleaned_sym,
                    "first_price": summary["first_open"],
                    "latest_price": summary["last_close"],
                    "price_change": summary["price_change"],
                    "percentage_change": summary["percentage_change"],
                    "period_high": summary["max_high"],
                    "period_low": summary["min_low"],
                    "total_volume": summary["total_volume"],
                    "record_count": summary["record_count"],
                }
            )

        return {
            "comparisons": results,
            "start_date": str(start_date) if start_date else None,
            "end_date": str(end_date) if end_date else None,
        }

    def execute_query_plan(self, plan: QueryPlan) -> dict[str, Any]:
        """
        Executes structured SQL retrieval based on a Phase 1 QueryPlan.
        """
        if "sql" not in plan.retrieval_sources:
            return {
                "status": "skipped",
                "message": "Query plan does not require SQL retrieval.",
                "data": None,
            }

        start_date = plan.date_range.start if plan.date_range else None
        end_date = plan.date_range.end if plan.date_range else None
        symbols = plan.asset_symbols

        if not symbols:
            # If no symbols specified in query plan, return available symbols info
            return {
                "status": "empty_symbols",
                "message": "No asset symbols identified in query plan.",
                "data": [],
            }

        if plan.intent == "market_comparison" or len(symbols) > 1:
            comparison = self.compare_market(symbols, start_date=start_date, end_date=end_date)
            return {
                "status": "success",
                "intent": plan.intent,
                "retrieval_type": "sql",
                "data": comparison,
            }

        # Single asset retrieval
        symbol = symbols[0]
        if start_date is not None or end_date is not None:
            # Time range query -> summary + recent price points
            summary = self.get_price_summary(symbol, start_date=start_date, end_date=end_date)
            history = self.get_price_history(
                symbol, start_date=start_date, end_date=end_date, limit=100
            )
            return {
                "status": "success",
                "intent": plan.intent,
                "retrieval_type": "sql",
                "data": {
                    "summary": summary,
                    "history": history,
                },
            }

        # Spot/latest price lookup
        latest = self.get_latest_price(symbol)
        return {
            "status": "success",
            "intent": plan.intent,
            "retrieval_type": "sql",
            "data": {
                "latest_price": latest,
            },
        }


price_service = PriceService()
