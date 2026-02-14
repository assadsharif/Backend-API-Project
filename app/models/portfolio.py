"""
Portfolio Tracking - Pydantic Models

Data models for portfolio management: holdings, requests, responses, and signals.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class PortfolioHolding(BaseModel):
    """A single ticker in a user's portfolio."""

    ticker: str = Field(..., pattern=r"^[A-Z]{1,5}$")
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Portfolio(BaseModel):
    """A user's complete portfolio."""

    user_id: str
    holdings: list[PortfolioHolding] = Field(default_factory=list)


class AddTickerRequest(BaseModel):
    """Request body for adding a ticker to portfolio."""

    ticker: str = Field(..., min_length=1)


class PortfolioResponse(BaseModel):
    """Response for GET /portfolio."""

    user_id: str
    holdings: list[PortfolioHolding]
    count: int
    max_holdings: int


class AddTickerResponse(BaseModel):
    """Response for POST /portfolio/add."""

    message: str
    ticker: str
    holdings: list[PortfolioHolding]
    count: int


class RemoveTickerResponse(BaseModel):
    """Response for DELETE /portfolio/remove/{ticker}."""

    message: str
    ticker: str
    holdings: list[PortfolioHolding]
    count: int


class PortfolioSignalResult(BaseModel):
    """Signal data for a single ticker in a portfolio signals response."""

    ticker: str
    signal: str | None = None
    confidence: int | None = None
    current_price: float | None = None
    error: str | None = None


class PortfolioSummary(BaseModel):
    """Aggregated portfolio metrics."""

    total_holdings: int = 0
    buy_count: int = 0
    sell_count: int = 0
    hold_count: int = 0
    error_count: int = 0


class PortfolioSignalsResponse(BaseModel):
    """Response for GET /portfolio/signals."""

    user_id: str
    signals: list[PortfolioSignalResult]
    summary: PortfolioSummary
    fetched_at: datetime
