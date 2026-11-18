from datetime import datetime, date
from pydantic import BaseModel, Field


class PriceRecord(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class PriceHistoryResponse(BaseModel):
    symbol: str
    count: int
    prices: list[PriceRecord]


class PriceSummary(BaseModel):
    symbol: str
    start_date: str | None = None
    end_date: str | None = None
    first_open: float | None = None
    last_close: float | None = None
    min_low: float | None = None
    max_high: float | None = None
    total_volume: float = 0.0
    price_change: float | None = None
    percentage_change: float | None = None
    record_count: int = 0


class MovingAverageRecord(BaseModel):
    timestamp: datetime
    close: float
    moving_average: float


class MovingAverageResponse(BaseModel):
    symbol: str
    window: int
    count: int
    records: list[MovingAverageRecord]


class MarketComparisonRequest(BaseModel):
    symbols: list[str] = Field(..., min_length=1, description="List of crypto symbols to compare")
    start_date: date | None = None
    end_date: date | None = None


class MarketComparisonItem(BaseModel):
    symbol: str
    first_price: float | None = None
    latest_price: float | None = None
    price_change: float | None = None
    percentage_change: float | None = None
    period_high: float | None = None
    period_low: float | None = None
    total_volume: float = 0.0
    record_count: int = 0


class MarketComparisonResponse(BaseModel):
    comparisons: list[MarketComparisonItem]
    start_date: str | None = None
    end_date: str | None = None
