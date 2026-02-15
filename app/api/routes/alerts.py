"""
Alerts & Notifications - Alert Endpoints

Manage alert rules and check triggered alerts.
All endpoints require authentication via X-API-Key header.
"""

import logging
from datetime import datetime, timezone
from typing import Union

from fastapi import APIRouter, Depends, Response

from app.api.dependencies import (
    check_rate_limit,
    get_alert_service,
    get_current_user,
    get_data_fetcher,
    get_portfolio_service,
    get_webhook_service,
)
from app.api.errors import InvalidTickerError, PortfolioRequiredError
from app.config import settings
from app.models.alert import (
    AlertDeleteResponse,
    AlertListResponse,
    AlertResponse,
    PriceThresholdCreate,
    PortfolioValueCreate,
    SignalChangeCreate,
    TriggeredAlertsResponse,
)
from app.models.user import RateLimitInfo, User
from app.services.alert_service import AlertService
from app.services.data_fetcher import DataFetcher
from app.services.indicator_calculator import IndicatorCalculator
from app.services.portfolio_service import PortfolioService
from app.services.webhook_service import WebhookService
from app.services.signal_generator import SignalGenerator
from app.utils.validators import TickerValidationError, validate_ticker

logger = logging.getLogger("app.api.routes.alerts")

router = APIRouter(prefix="/alerts", tags=["Alerts"])

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


# --- T015: GET /alerts/triggered must be registered BEFORE GET /alerts
#     to prevent FastAPI from matching "triggered" as an {alert_id} path param ---


@router.get("/triggered", response_model=TriggeredAlertsResponse)
async def get_triggered_alerts(
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service),
    data_fetcher: DataFetcher = Depends(get_data_fetcher),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> TriggeredAlertsResponse:
    """Check all alerts for the authenticated user and return evaluation results."""
    now = datetime.now(timezone.utc)

    # Get portfolio holdings for portfolio_value alerts
    portfolio = portfolio_service.get_portfolio(current_user.id)
    holdings = [h.ticker for h in portfolio.holdings]

    results, summary = await alert_service.check_triggered_alerts(
        user_id=current_user.id,
        data_fetcher=data_fetcher,
        indicator_calculator=_indicator_calculator,
        signal_generator=_signal_generator,
        portfolio_holdings=holdings,
    )

    _inject_rate_limit_headers(response, rate_limit_info)

    logger.info(
        "Triggered alerts checked for user %s: %d total, %d triggered, %d errors",
        current_user.id,
        summary.total_alerts,
        summary.triggered_count,
        summary.error_count,
    )

    # Deliver triggered alerts to webhook if configured
    if summary.triggered_count > 0:
        try:
            config = webhook_service.get_config(current_user.id)
            if config is not None and config.is_active:
                payload = webhook_service.build_payload(
                    current_user.id, results, now
                )
                webhook_service.deliver(
                    current_user.id, payload, config.url, config.secret
                )
        except Exception:
            logger.exception(
                "Webhook delivery failed for user %s (non-fatal)",
                current_user.id,
            )

    return TriggeredAlertsResponse(
        user_id=current_user.id,
        results=results,
        summary=summary,
        evaluated_at=now,
    )


@router.post("", response_model=AlertResponse, status_code=201)
async def create_alert(
    body: Union[PriceThresholdCreate, SignalChangeCreate, PortfolioValueCreate],
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    data_fetcher: DataFetcher = Depends(get_data_fetcher),
) -> AlertResponse:
    """Create a new alert for the authenticated user."""
    alert_data = body.model_dump()

    # Validate ticker for types that require it
    if hasattr(body, "ticker"):
        try:
            normalized = validate_ticker(body.ticker)
            alert_data["ticker"] = normalized
        except TickerValidationError:
            raise InvalidTickerError(body.ticker)

    # For portfolio_value: verify user has a portfolio and compute baseline
    if body.alert_type == "portfolio_value":
        portfolio = portfolio_service.get_portfolio(current_user.id)
        if not portfolio.holdings:
            raise PortfolioRequiredError()

        # Compute baseline portfolio value
        total_value = 0.0
        for holding in portfolio.holdings:
            try:
                df = await data_fetcher.fetch_historical_data(holding.ticker)
                price = float(df["Close"].iloc[-1])
                total_value += price
            except Exception as exc:
                logger.warning(
                    "Failed to fetch price for %s during baseline calc: %s",
                    holding.ticker, exc,
                )
        alert_data["baseline_value"] = total_value

    alert = alert_service.create_alert(current_user.id, alert_data)

    _inject_rate_limit_headers(response, rate_limit_info)

    logger.info(
        "User %s created %s alert (id=%s)",
        current_user.id, alert.alert_type.value, alert.id,
    )

    return AlertResponse(
        id=alert.id,
        alert_type=alert.alert_type,
        ticker=alert.ticker,
        target_price=alert.target_price,
        price_direction=alert.price_direction,
        target_signal=alert.target_signal,
        percentage_threshold=alert.percentage_threshold,
        baseline_value=alert.baseline_value,
        created_at=alert.created_at,
    )


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service),
) -> AlertListResponse:
    """List all active alerts for the authenticated user."""
    alerts = alert_service.list_alerts(current_user.id)
    _inject_rate_limit_headers(response, rate_limit_info)

    return AlertListResponse(
        user_id=current_user.id,
        alerts=alerts,
        count=len(alerts),
        max_alerts=settings.ALERTS_MAX_PER_USER,
    )


@router.delete("/{alert_id}", response_model=AlertDeleteResponse)
async def delete_alert(
    alert_id: str,
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service),
) -> AlertDeleteResponse:
    """Delete an alert by its ID. Only the alert owner can delete it."""
    alert_service.delete_alert(current_user.id, alert_id)
    _inject_rate_limit_headers(response, rate_limit_info)

    logger.info("User %s deleted alert %s", current_user.id, alert_id)

    return AlertDeleteResponse(alert_id=alert_id)
