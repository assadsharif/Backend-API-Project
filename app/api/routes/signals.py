"""
Stock Signal API - Signal Endpoint

GET /signal/{ticker} — Returns a BUY/SELL/HOLD trading signal.
Implements T020-T023: endpoint, caching, error handling, graceful degradation.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response

from ...models.signal import Signal
from ...models.user import RateLimitInfo
from ...services.cache_service import CacheService
from ...services.data_fetcher import DataFetcher
from ...services.indicator_calculator import IndicatorCalculator
from ...services.signal_generator import SignalGenerator
from ...utils.validators import TickerValidationError, validate_ticker
from ..dependencies import check_rate_limit, get_cache_service, get_current_user, get_data_fetcher
from ..errors import InvalidTickerError

logger = logging.getLogger("app.api.signals")

router = APIRouter(tags=["signals"])

# Service singletons (stateless, safe to share)
_indicator_calculator = IndicatorCalculator()
_signal_generator = SignalGenerator()


@router.get(
    "/signal/{ticker}",
    response_model=Signal,
    response_model_by_alias=True,
    summary="Get trading signal for a stock",
    responses={
        400: {"description": "Invalid ticker symbol"},
        404: {"description": "Ticker not found"},
        503: {"description": "Data source unavailable"},
    },
)
async def get_signal(
    ticker: str,
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    cache: CacheService = Depends(get_cache_service),
    data_fetcher: DataFetcher = Depends(get_data_fetcher),
) -> Signal:
    """
    Generate a BUY/SELL/HOLD trading signal for the given stock ticker.

    Calculates RSI, MACD, SMA, and EMA indicators from historical price data,
    then applies a rule-based scoring algorithm to produce a signal with
    confidence level and human-readable reasoning.

    Results are cached for 15 minutes (configurable).
    """
    # T022: Validate ticker — raises InvalidTickerError (400)
    try:
        ticker = validate_ticker(ticker)
    except TickerValidationError:
        raise InvalidTickerError(ticker)

    # T021: Check cache first
    cache_key = f"signal:{ticker}"
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Cache hit for %s", ticker)
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info.limit)
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_info.remaining)
        response.headers["X-RateLimit-Reset"] = str(int(rate_limit_info.reset_at.timestamp()))
        return cached

    # Fetch historical data — raises TickerNotFoundError (404) or
    # DataSourceUnavailableError (503) from data_fetcher
    df = await data_fetcher.fetch_historical_data(ticker)

    # Calculate indicators
    indicators = _indicator_calculator.calculate(df)
    current_price = _indicator_calculator.get_current_price(df)
    data_freshness_ts = _indicator_calculator.get_data_freshness(df)

    # T023: Track data days for graceful degradation reasoning
    data_days = len(df)

    # Generate signal
    result = _signal_generator.generate(indicators, current_price)
    reasoning = _signal_generator.build_reasoning(
        result, indicators, current_price, data_days=data_days
    )

    now = datetime.now(timezone.utc)
    # Convert pandas Timestamp to Python datetime
    if hasattr(data_freshness_ts, "to_pydatetime"):
        freshness_dt = data_freshness_ts.to_pydatetime()
        if freshness_dt.tzinfo is None:
            freshness_dt = freshness_dt.replace(tzinfo=timezone.utc)
    else:
        freshness_dt = now

    signal = Signal(
        ticker=ticker,
        signal=result.action,
        confidence=result.confidence,
        reasoning=reasoning,
        timestamp=now,
        data_freshness=freshness_dt,
        current_price=current_price,
        indicators=indicators,
    )

    # Store in cache
    cache.set(cache_key, signal)
    logger.info(
        "Signal generated for %s: %s (confidence=%d, score=%d)",
        ticker,
        result.action.value,
        result.confidence,
        result.score,
    )

    # Inject rate limit headers
    response.headers["X-RateLimit-Limit"] = str(rate_limit_info.limit)
    response.headers["X-RateLimit-Remaining"] = str(rate_limit_info.remaining)
    response.headers["X-RateLimit-Reset"] = str(int(rate_limit_info.reset_at.timestamp()))

    return signal
