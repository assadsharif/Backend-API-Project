"""
Alerts & Notifications - Alert Models

Pydantic models for alert creation, storage, and triggered-alert evaluation.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class AlertType(str, Enum):
    """Supported alert types."""

    PRICE_THRESHOLD = "price_threshold"
    SIGNAL_CHANGE = "signal_change"
    PORTFOLIO_VALUE = "portfolio_value"


class PriceDirection(str, Enum):
    """Direction for price threshold alerts."""

    ABOVE = "above"
    BELOW = "below"


class SignalTarget(str, Enum):
    """Target signal for signal change alerts."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


# --- Request schemas (discriminated union by alert_type) ---


class PriceThresholdCreate(BaseModel):
    """Request body for creating a price threshold alert."""

    alert_type: Literal["price_threshold"]
    ticker: str = Field(..., min_length=1, max_length=5)
    target_price: float = Field(..., gt=0)
    price_direction: PriceDirection


class SignalChangeCreate(BaseModel):
    """Request body for creating a signal change alert."""

    alert_type: Literal["signal_change"]
    ticker: str = Field(..., min_length=1, max_length=5)
    target_signal: SignalTarget


class PortfolioValueCreate(BaseModel):
    """Request body for creating a portfolio value alert."""

    alert_type: Literal["portfolio_value"]
    percentage_threshold: float = Field(..., gt=0)


AlertCreate = Annotated[
    Union[PriceThresholdCreate, SignalChangeCreate, PortfolioValueCreate],
    Field(discriminator="alert_type"),
]


# --- Persisted entity ---


class Alert(BaseModel):
    """Persisted alert entity stored in data/alerts.json."""

    id: str
    user_id: str
    alert_type: AlertType
    ticker: str | None = None
    target_price: float | None = None
    price_direction: PriceDirection | None = None
    target_signal: SignalTarget | None = None
    percentage_threshold: float | None = None
    baseline_value: float | None = None
    created_at: datetime


# --- Response schemas ---


class AlertResponse(BaseModel):
    """Response for POST /alerts (alert creation)."""

    id: str
    alert_type: AlertType
    ticker: str | None = None
    target_price: float | None = None
    price_direction: PriceDirection | None = None
    target_signal: SignalTarget | None = None
    percentage_threshold: float | None = None
    baseline_value: float | None = None
    created_at: datetime
    message: str = "Alert created successfully"


class AlertListResponse(BaseModel):
    """Response for GET /alerts."""

    user_id: str
    alerts: list[Alert]
    count: int
    max_alerts: int


class AlertDeleteResponse(BaseModel):
    """Response for DELETE /alerts/{alert_id}."""

    message: str = "Alert deleted successfully"
    alert_id: str


# --- Triggered alert evaluation ---


class AlertSummaryInfo(BaseModel):
    """Minimal alert info included in triggered results."""

    id: str
    alert_type: AlertType
    ticker: str | None = None
    target_price: float | None = None
    price_direction: PriceDirection | None = None
    target_signal: SignalTarget | None = None
    percentage_threshold: float | None = None
    baseline_value: float | None = None


class TriggeredAlertResult(BaseModel):
    """Single alert evaluation result."""

    alert: AlertSummaryInfo
    triggered: bool = False
    current_value: str | None = None
    details: str | None = None
    error: str | None = None
    evaluated_at: datetime


class TriggeredAlertsSummary(BaseModel):
    """Summary counts for triggered alerts response."""

    total_alerts: int = 0
    triggered_count: int = 0
    not_triggered_count: int = 0
    error_count: int = 0


class TriggeredAlertsResponse(BaseModel):
    """Response for GET /alerts/triggered."""

    user_id: str
    results: list[TriggeredAlertResult]
    summary: TriggeredAlertsSummary
    evaluated_at: datetime
