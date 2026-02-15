"""
Webhooks & Notifications - Webhook Models

Pydantic models for webhook configuration, delivery tracking,
and request/response schemas.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class DeliveryStatus(str, Enum):
    """Status of a webhook delivery attempt."""

    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"


# --- Persisted entities ---


class WebhookConfig(BaseModel):
    """Persisted webhook configuration for a user."""

    url: str
    secret: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class WebhookDelivery(BaseModel):
    """Persisted webhook delivery attempt record."""

    id: str
    event: str
    status: DeliveryStatus
    url: str
    payload_summary: str
    http_status: int | None = None
    attempts: int = 1
    failure_reason: str | None = None
    created_at: datetime
    completed_at: datetime


# --- Request schemas ---


class WebhookCreateRequest(BaseModel):
    """Request body for POST /webhooks."""

    url: str
    secret: str | None = None


# --- Response schemas ---


class WebhookConfigResponse(BaseModel):
    """Response for POST /webhooks and GET /webhooks."""

    url: str | None = None
    has_secret: bool = False
    is_active: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    message: str | None = None


class WebhookDeleteResponse(BaseModel):
    """Response for DELETE /webhooks."""

    message: str = "Webhook deleted successfully"


class WebhookHistoryResponse(BaseModel):
    """Response for GET /webhooks/history."""

    user_id: str
    deliveries: list[WebhookDelivery]
    count: int
    max_records: int


class WebhookPayload(BaseModel):
    """Payload sent to webhook URLs."""

    event: str = "alerts.triggered"
    user_id: str
    triggered_alerts: list[dict]
    triggered_count: int
    evaluated_at: datetime
