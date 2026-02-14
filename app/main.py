"""
Stock Signal API - FastAPI Application Entry Point

Main application module that initializes FastAPI with middleware,
routers, and error handlers.
"""

import logging
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_error_handlers
from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.indicators import router as indicators_router
from app.api.routes.signals import router as signals_router
from app.config import settings
from app.utils.logging import setup_logging

# Application metadata
APP_VERSION = "1.0.0"
APP_TITLE = "Stock Signal API"
APP_DESCRIPTION = """
REST API for stock trading signals based on technical analysis.

Provides buy/sell/hold recommendations with confidence levels and reasoning
based on technical indicators (RSI, MACD, SMA, EMA) calculated from historical price data.

**Data Source**: Yahoo Finance (15-minute delay)
**Supported Markets**: US stocks only (NYSE, NASDAQ)
**Cache TTL**: 15 minutes
"""

# Configure structured JSON logging
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger("app.main")

# Create FastAPI application
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# T042: Response time tracking middleware
@app.middleware("http")
async def response_time_middleware(request: Request, call_next) -> Response:
    """Track and log response time for every request."""
    start = time.perf_counter()
    response: Response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Response-Time-Ms"] = str(elapsed_ms)
    logger.info(
        "%s %s -> %s (%.2fms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
        extra={
            "response_time_ms": elapsed_ms,
            "status_code": response.status_code,
        },
    )
    return response


# Register error handlers
register_error_handlers(app)

# Register routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(signals_router)
app.include_router(indicators_router)
app.include_router(admin_router)


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint - API information."""
    return {
        "name": APP_TITLE,
        "version": APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
    }


# Startup event
@app.on_event("startup")
async def startup_event() -> None:
    """Initialize services on startup."""
    logger.info("Starting %s v%s", APP_TITLE, APP_VERSION)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    logger.info("Shutting down %s", APP_TITLE)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
