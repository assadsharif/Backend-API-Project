"""
Stock Signal API - FastAPI Application Entry Point

Main application module that initializes FastAPI with middleware,
routers, and error handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_error_handlers
from app.api.routes.health import router as health_router

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


# Register error handlers
register_error_handlers(app)

# Register routers
app.include_router(health_router)


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
    print(f"Starting {APP_TITLE} v{APP_VERSION}")
    print("API documentation available at /docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    print(f"Shutting down {APP_TITLE}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
