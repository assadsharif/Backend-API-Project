"""
Webhooks & Notifications - Webhook Endpoints

Manage webhook configuration and view delivery history.
All endpoints require authentication via X-API-Key header.
"""

import logging

from fastapi import APIRouter, Depends, Response

from app.api.dependencies import (
    check_rate_limit,
    get_current_user,
    get_webhook_service,
)
from app.config import settings
from app.models.user import RateLimitInfo, User
from app.models.webhook import (
    WebhookConfigResponse,
    WebhookCreateRequest,
    WebhookDeleteResponse,
    WebhookHistoryResponse,
)
from app.services.webhook_service import WebhookService

logger = logging.getLogger("app.api.routes.webhooks")

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def _inject_rate_limit_headers(
    response: Response, rate_limit_info: RateLimitInfo
) -> None:
    """Set rate limit headers on the response."""
    response.headers["X-RateLimit-Limit"] = str(rate_limit_info.limit)
    response.headers["X-RateLimit-Remaining"] = str(rate_limit_info.remaining)
    response.headers["X-RateLimit-Reset"] = str(
        int(rate_limit_info.reset_at.timestamp())
    )


# --- GET /webhooks/history must be registered BEFORE any parameterized routes ---


@router.get("/history", response_model=WebhookHistoryResponse)
async def get_webhook_history(
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> WebhookHistoryResponse:
    """Retrieve recent webhook delivery attempts for the authenticated user."""
    deliveries = webhook_service.get_deliveries(current_user.id)
    _inject_rate_limit_headers(response, rate_limit_info)

    logger.info(
        "Webhook history retrieved for user %s: %d deliveries",
        current_user.id,
        len(deliveries),
    )

    return WebhookHistoryResponse(
        user_id=current_user.id,
        deliveries=deliveries,
        count=len(deliveries),
        max_records=settings.WEBHOOK_MAX_DELIVERIES,
    )


@router.post("", response_model=WebhookConfigResponse)
async def register_webhook(
    body: WebhookCreateRequest,
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> WebhookConfigResponse:
    """Register or replace a webhook URL for the authenticated user."""
    config, is_new = webhook_service.set_config(
        current_user.id, body.url, body.secret
    )
    _inject_rate_limit_headers(response, rate_limit_info)

    if is_new:
        response.status_code = 201
        message = "Webhook registered successfully"
    else:
        response.status_code = 200
        message = "Webhook updated successfully"

    logger.info(
        "User %s %s webhook: url=%s has_secret=%s",
        current_user.id,
        "registered" if is_new else "updated",
        config.url,
        config.secret is not None,
    )

    return WebhookConfigResponse(
        url=config.url,
        has_secret=config.secret is not None,
        is_active=config.is_active,
        created_at=config.created_at,
        updated_at=config.updated_at,
        message=message,
    )


@router.get("", response_model=WebhookConfigResponse)
async def get_webhook(
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> WebhookConfigResponse:
    """Retrieve the current webhook configuration for the authenticated user."""
    config = webhook_service.get_config(current_user.id)
    _inject_rate_limit_headers(response, rate_limit_info)

    if config is None:
        return WebhookConfigResponse(
            url=None,
            has_secret=False,
            is_active=False,
            message="No webhook configured",
        )

    return WebhookConfigResponse(
        url=config.url,
        has_secret=config.secret is not None,
        is_active=config.is_active,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.delete("", response_model=WebhookDeleteResponse)
async def delete_webhook(
    response: Response,
    rate_limit_info: RateLimitInfo = Depends(check_rate_limit),
    current_user: User = Depends(get_current_user),
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> WebhookDeleteResponse:
    """Delete the webhook configuration for the authenticated user."""
    webhook_service.delete_config(current_user.id)
    _inject_rate_limit_headers(response, rate_limit_info)

    logger.info("User %s deleted webhook", current_user.id)

    return WebhookDeleteResponse()
