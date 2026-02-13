"""
Stock Signal API - Health Check Endpoint

GET /health — returns service health status and data source availability
per openapi.yaml HealthResponse schema.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ...config import settings
from ..dependencies import get_data_fetcher
from ...services.data_fetcher import DataFetcher

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    data_fetcher: DataFetcher = Depends(get_data_fetcher),
) -> JSONResponse:
    """
    Health check endpoint.

    Returns service status, API version, and data source availability.
    Returns 200 if healthy, 503 if degraded/unhealthy.
    """
    now = datetime.now(timezone.utc)

    # Check data source availability
    source_available = await data_fetcher.check_availability()
    last_check = data_fetcher.last_check_time or now

    status = "healthy" if source_available else "degraded"
    status_code = 200 if source_available else 503

    body = {
        "status": status,
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "version": settings.API_VERSION,
        "data_source": {
            "provider": settings.DATA_SOURCE,
            "status": "available" if source_available else "unavailable",
            "last_check": last_check.isoformat().replace("+00:00", "Z"),
        },
    }

    return JSONResponse(status_code=status_code, content=body)
