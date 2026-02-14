"""
Portfolio Tracking - Portfolio Endpoints

Manage portfolio holdings and fetch signals for all holdings.
All endpoints require authentication via X-API-Key header.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response

from app.api.dependencies import (
    check_rate_limit,
    get_cache_service,
    get_current_user,
    get_data_fetcher,
    get_portfolio_service,
)
from app.api.errors import InvalidTickerError
from app.config import settings
from app.models.portfolio import (
    AddTickerRequest,
    AddTickerResponse,
    PortfolioResponse,
    PortfolioSignalResult,
    PortfolioSignalsResponse,
    PortfolioSummary,
    RemoveTickerResponse,
)
from app.models.user import RateLimitInfo, User
from app.services.cache_service import CacheService
from app.services.data_fetcher import DataFetcher
from app.services.indicator_calculator import IndicatorCalculator
from app.services.portfolio_service import PortfolioService
from app.services.signal_generator import SignalGenerator
from app.utils.validators import TickerValidationError, validate_ticker

logger = logging.getLogger("app.api.routes.portfolio")

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

# Reuse existing signal pipeline singletons
_indicator_calculator = IndicatorCalculator()
_signal_generator = SignalGenerator()


def _inject_rate_limit_headers(
    response: Response, rate_limit_info: RateLimitInfo
) -> None:
    """Set rate limit headers on the response."""
    response.headers["X-RateLimit-Limit"] = str(rate_limit_info.limit)
    response.headers["X-RateLimit-Remaining"] = str(rate_limit_info.remaining)
    response.headers["X-RateLimit-Reset"] = str(
        int(rate_limit_info.reset_at.timestamp())
    )


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> PortfolioResponse:
    """List all holdings in the authenticated user's portfolio."""
    portfolio = portfolio_service.get_portfolio(current_user.id)
    _inject_rate_limit_headers(response, rate_limit_info)
    return PortfolioResponse(
        user_id=current_user.id,
        holdings=portfolio.holdings,
        count=len(portfolio.holdings),
        max_holdings=settings.PORTFOLIO_MAX_HOLDINGS,
    )


@router.post("/add", response_model=AddTickerResponse)
async def add_ticker(
    body: AddTickerRequest,
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> AddTickerResponse:
    """Add a stock ticker to the authenticated user's portfolio."""
    # Validate ticker format using existing validator
    try:
        normalized = validate_ticker(body.ticker)
    except TickerValidationError:
        raise InvalidTickerError(body.ticker)

    portfolio = portfolio_service.add_ticker(current_user.id, normalized)
    _inject_rate_limit_headers(response, rate_limit_info)
    logger.info("User %s added %s to portfolio", current_user.id, normalized)
    return AddTickerResponse(
        message=f"{normalized} added to portfolio.",
        ticker=normalized,
        holdings=portfolio.holdings,
        count=len(portfolio.holdings),
    )


@router.delete("/remove/{ticker}", response_model=RemoveTickerResponse)
async def remove_ticker(
    ticker: str,
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
) -> RemoveTickerResponse:
    """Remove a stock ticker from the authenticated user's portfolio."""
    try:
        normalized = validate_ticker(ticker)
    except TickerValidationError:
        raise InvalidTickerError(ticker)

    portfolio = portfolio_service.remove_ticker(current_user.id, normalized)
    _inject_rate_limit_headers(response, rate_limit_info)
    logger.info("User %s removed %s from portfolio", current_user.id, normalized)
    return RemoveTickerResponse(
        message=f"{normalized} removed from portfolio.",
        ticker=normalized,
        holdings=portfolio.holdings,
        count=len(portfolio.holdings),
    )


@router.get("/signals", response_model=PortfolioSignalsResponse)
async def get_portfolio_signals(
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    cache: CacheService = Depends(get_cache_service),
    data_fetcher: DataFetcher = Depends(get_data_fetcher),
) -> PortfolioSignalsResponse:
    """Fetch trading signals for all portfolio holdings.

    Returns partial results — individual ticker failures don't fail the request.
    Includes a summary with signal sentiment breakdown.
    """
    portfolio = portfolio_service.get_portfolio(current_user.id)
    signals: list[PortfolioSignalResult] = []

    for holding in portfolio.holdings:
        ticker = holding.ticker
        try:
            # Check cache first
            cache_key = f"signal:{ticker}"
            cached = cache.get(cache_key)
            if cached is not None:
                signals.append(
                    PortfolioSignalResult(
                        ticker=ticker,
                        signal=cached.signal.value,
                        confidence=cached.confidence,
                        current_price=cached.current_price,
                    )
                )
                continue

            # Fetch and compute signal
            df = await data_fetcher.fetch_historical_data(ticker)
            indicators = _indicator_calculator.calculate(df)
            current_price = _indicator_calculator.get_current_price(df)
            result = _signal_generator.generate(indicators, current_price)

            signals.append(
                PortfolioSignalResult(
                    ticker=ticker,
                    signal=result.action.value,
                    confidence=result.confidence,
                    current_price=current_price,
                )
            )
        except Exception as exc:
            logger.warning(
                "Failed to fetch signal for %s: %s", ticker, str(exc)
            )
            signals.append(
                PortfolioSignalResult(
                    ticker=ticker,
                    error=str(exc),
                )
            )

    # Compute summary
    buy_count = sum(1 for s in signals if s.signal == "BUY")
    sell_count = sum(1 for s in signals if s.signal == "SELL")
    hold_count = sum(1 for s in signals if s.signal == "HOLD")
    error_count = sum(1 for s in signals if s.error is not None)

    summary = PortfolioSummary(
        total_holdings=len(portfolio.holdings),
        buy_count=buy_count,
        sell_count=sell_count,
        hold_count=hold_count,
        error_count=error_count,
    )

    _inject_rate_limit_headers(response, rate_limit_info)

    logger.info(
        "Portfolio signals fetched for user %s: %d tickers (%d errors)",
        current_user.id,
        len(signals),
        error_count,
    )

    return PortfolioSignalsResponse(
        user_id=current_user.id,
        signals=signals,
        summary=summary,
        fetched_at=datetime.now(timezone.utc),
    )
