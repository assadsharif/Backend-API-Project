"""
Stock Signal API - Indicators Endpoint

GET /indicators/{ticker} — Returns technical indicators without a trading signal.
Implements T027-T030: endpoint, reuse IndicatorCalculator, caching, error handling.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response

from ...models.indicator import IndicatorResponse
from ...models.user import RateLimitInfo
from ...services.cache_service import CacheService
from ...services.data_fetcher import DataFetcher
from ...services.indicator_calculator import IndicatorCalculator
from ...utils.validators import TickerValidationError, validate_ticker
from ..dependencies import check_rate_limit, get_cache_service, get_data_fetcher
from ..errors import InvalidTickerError

logger = logging.getLogger("app.api.indicators")

router = APIRouter(tags=["indicators"])

_indicator_calculator = IndicatorCalculator()


@router.get(
    "/indicators/{ticker}",
    response_model=IndicatorResponse,
    response_model_by_alias=True,
    summary="Get technical indicators for a stock",
    responses={
        400: {"description": "Invalid ticker symbol"},
        404: {"description": "Ticker not found"},
        503: {"description": "Data source unavailable"},
    },
)
async def get_indicators(
    ticker: str,
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    cache: CacheService = Depends(get_cache_service),
    data_fetcher: DataFetcher = Depends(get_data_fetcher),
) -> IndicatorResponse:
    """
    Return calculated technical indicators (RSI, MACD, SMA, EMA) for a stock.

    Provides transparency into the raw indicator values without generating
    a trading signal. Useful for custom analysis.

    Results are cached for 15 minutes (configurable).
    """
    # Validate ticker
    try:
        ticker = validate_ticker(ticker)
    except TickerValidationError:
        raise InvalidTickerError(ticker)

    # Check cache
    cache_key = f"indicators:{ticker}"
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Cache hit for indicators:%s", ticker)
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info.limit)
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_info.remaining)
        response.headers["X-RateLimit-Reset"] = str(int(rate_limit_info.reset_at.timestamp()))
        return cached

    # Fetch historical data (raises 404 / 503 from data_fetcher)
    df = await data_fetcher.fetch_historical_data(ticker)

    # Calculate indicators
    indicators = _indicator_calculator.calculate(df)
    current_price = _indicator_calculator.get_current_price(df)

    now = datetime.now(timezone.utc)

    indicator_response = IndicatorResponse(
        ticker=ticker,
        calculated_at=now,
        current_price=current_price,
        indicators=indicators,
    )

    # Store in cache
    cache.set(cache_key, indicator_response)
    logger.info("Indicators calculated for %s", ticker)

    # Inject rate limit headers
    response.headers["X-RateLimit-Limit"] = str(rate_limit_info.limit)
    response.headers["X-RateLimit-Remaining"] = str(rate_limit_info.remaining)
    response.headers["X-RateLimit-Reset"] = str(int(rate_limit_info.reset_at.timestamp()))

    return indicator_response
