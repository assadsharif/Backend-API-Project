"""
Stock Signal API - FastAPI Dependency Injection

Provides singleton service instances via FastAPI's dependency injection system.
"""

from functools import lru_cache

from ..config import Settings, settings
from ..services.cache_service import CacheService
from ..services.data_fetcher import DataFetcher


@lru_cache
def get_settings() -> Settings:
    """Return the application settings singleton."""
    return settings


# Service singletons (created once, reused across requests)
_cache_service: CacheService | None = None
_data_fetcher: DataFetcher | None = None


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
