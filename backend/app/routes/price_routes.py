from datetime import date
from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.prices import (
    MarketComparisonRequest,
    MarketComparisonResponse,
    MovingAverageResponse,
    PriceHistoryResponse,
    PriceRecord,
    PriceSummary,
)
from backend.app.schemas.query_plan import QueryPlan
from backend.app.services.prices_services import price_service

router = APIRouter(prefix="/prices", tags=["Prices & Analytics"])


@router.get(
    "/latest",
    response_model=PriceRecord | None,
    summary="Get latest price candle for an asset",
)
def get_latest_price(
    symbol: str = Query(..., min_length=1, description="Ticker symbol (e.g. BTC-USD)"),
) -> PriceRecord | None:
    try:
        record = price_service.get_latest_price(symbol)
        return PriceRecord(**record) if record else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")


@router.get(
    "/history",
    response_model=PriceHistoryResponse,
    summary="Get historical OHLCV price series",
)
def get_price_history(
    symbol: str = Query(..., min_length=1, description="Ticker symbol (e.g. BTC-USD)"),
    start_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(default=1000, ge=1, le=5000, description="Max candles to retrieve"),
) -> PriceHistoryResponse:
    try:
        if start_date and end_date and end_date < start_date:
            raise HTTPException(status_code=400, detail="End date cannot be earlier than start date.")
        data = price_service.get_price_history(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
        return PriceHistoryResponse(**data)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")


@router.get(
    "/summary",
    response_model=PriceSummary,
    summary="Get aggregated statistics and price changes over an interval",
)
def get_price_summary(
    symbol: str = Query(..., min_length=1, description="Ticker symbol (e.g. BTC-USD)"),
    start_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
) -> PriceSummary:
    try:
        if start_date and end_date and end_date < start_date:
            raise HTTPException(status_code=400, detail="End date cannot be earlier than start date.")
        data = price_service.get_price_summary(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )
        return PriceSummary(**data)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")


@router.get(
    "/moving-average",
    response_model=MovingAverageResponse,
    summary="Calculate rolling simple moving averages (SMA)",
)
def get_moving_average(
    symbol: str = Query(..., min_length=1, description="Ticker symbol (e.g. BTC-USD)"),
    window: int = Query(default=7, ge=1, le=365, description="Window size in periods/days"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max data points to retrieve"),
) -> MovingAverageResponse:
    try:
        data = price_service.get_moving_average(symbol=symbol, window=window, limit=limit)
        return MovingAverageResponse(**data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")


@router.post(
    "/compare",
    response_model=MarketComparisonResponse,
    summary="Compare performance across multiple assets",
)
def compare_market(request: MarketComparisonRequest) -> MarketComparisonResponse:
    try:
        if request.start_date and request.end_date and request.end_date < request.start_date:
            raise HTTPException(status_code=400, detail="End date cannot be earlier than start date.")
        data = price_service.compare_market(
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        return MarketComparisonResponse(**data)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")


@router.post(
    "/execute-plan",
    summary="Execute SQL retrieval for a planned query",
)
def execute_query_plan(plan: QueryPlan):
    try:
        return price_service.execute_query_plan(plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan execution error: {str(e)}")
