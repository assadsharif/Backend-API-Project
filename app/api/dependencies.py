"""
Stock Signal API - FastAPI Dependency Injection

Provides singleton service instances via FastAPI's dependency injection system.
"""

import logging
from functools import lru_cache

from fastapi import Header

from ..config import Settings, settings
from fastapi import Depends

from ..models.user import RateLimitInfo, User
from ..services.cache_service import CacheService
from ..services.data_fetcher import DataFetcher
from ..services.rate_limiter import RateLimiter
from ..services.alert_service import AlertService
from ..services.portfolio_service import PortfolioService
from ..services.user_service import UserService
from ..services.webhook_service import WebhookService
from .errors import AccountDisabledError, AdminNotConfiguredError, AuthenticationError

logger = logging.getLogger("app.api.dependencies")


@lru_cache
def get_settings() -> Settings:
    """Return the application settings singleton."""
    return settings


# Service singletons (created once, reused across requests)
_cache_service: CacheService | None = None
_data_fetcher: DataFetcher | None = None
_user_service: UserService | None = None
_rate_limiter: RateLimiter | None = None
_portfolio_service: PortfolioService | None = None
_alert_service: AlertService | None = None
_webhook_service: WebhookService | None = None


def get_cache_service() -> CacheService:
    """Return the CacheService singleton."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService(
            maxsize=settings.CACHE_MAX_SIZE,
            ttl=settings.CACHE_TTL,
        )
    return _cache_service


def get_data_fetcher() -> DataFetcher:
    """Return the DataFetcher singleton."""
    global _data_fetcher
    if _data_fetcher is None:
        _data_fetcher = DataFetcher(
            historical_days=settings.HISTORICAL_DAYS,
            max_retries=settings.MAX_RETRIES,
            retry_delay=settings.RETRY_DELAY,
            retry_backoff=settings.RETRY_BACKOFF,
        )
    return _data_fetcher


def get_user_service() -> UserService:
    """Return the UserService singleton."""
    global _user_service
    if _user_service is None:
        _user_service = UserService(data_file=settings.USER_DATA_FILE)
    return _user_service


def get_rate_limiter() -> RateLimiter:
    """Return the RateLimiter singleton."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(
            max_requests=settings.RATE_LIMIT_MAX_REQUESTS,
            window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
        )
    return _rate_limiter


def get_portfolio_service() -> PortfolioService:
    """Return the PortfolioService singleton."""
    global _portfolio_service
    if _portfolio_service is None:
        _portfolio_service = PortfolioService(
            data_file=settings.PORTFOLIO_DATA_FILE,
            max_holdings=settings.PORTFOLIO_MAX_HOLDINGS,
        )
    return _portfolio_service


def get_alert_service() -> AlertService:
    """Return the AlertService singleton."""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService(
            data_file=settings.ALERTS_DATA_FILE,
            max_per_user=settings.ALERTS_MAX_PER_USER,
        )
    return _alert_service


def get_webhook_service() -> WebhookService:
    """Return the WebhookService singleton."""
    global _webhook_service
    if _webhook_service is None:
        _webhook_service = WebhookService(
            data_file=settings.WEBHOOK_DATA_FILE,
            max_deliveries=settings.WEBHOOK_MAX_DELIVERIES,
        )
    return _webhook_service


def get_current_user(x_api_key: str = Header()) -> User:
    """Validate API key and return the authenticated user.

    Raises AuthenticationError if key is missing/invalid.
    Raises AccountDisabledError if user account is disabled.
    """
    user_service = get_user_service()
    user = user_service.get_user_by_api_key(x_api_key)
    if user is None:
        logger.warning("Auth failed: invalid API key (key=%.8s...)", x_api_key)
        raise AuthenticationError()
    if user.status.value == "disabled":
        logger.warning("Auth failed: disabled account (user_id=%s)", user.id)
        raise AccountDisabledError()
    logger.debug("Auth success: user_id=%s", user.id)
    return user


def check_rate_limit(
    current_user: User = Depends(get_current_user),
) -> RateLimitInfo:
    """Check rate limit for the authenticated user.

    Returns RateLimitInfo with remaining quota.
    Raises RateLimitExceededError if limit exceeded.
    """
    rate_limiter = get_rate_limiter()
    return rate_limiter.check_rate_limit(current_user.api_key)


def require_admin(x_admin_key: str = Header()) -> str:
    """Validate admin key. Returns the admin key on success.

    Raises AdminNotConfiguredError if ADMIN_API_KEY is not set.
    Raises AuthenticationError if the provided key doesn't match.
    """
    if settings.ADMIN_API_KEY is None:
        raise AdminNotConfiguredError()
    if x_admin_key != settings.ADMIN_API_KEY:
        raise AuthenticationError("Invalid admin key.")
    return x_admin_key
