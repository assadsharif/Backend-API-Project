"""
User Authentication - Admin Endpoints

Admin-only endpoints for user management.
Protected by X-Admin-Key header.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_user_service, require_admin
from app.models.user import (
    AdminKeyRegenerateResponse,
    UserDetailResponse,
    UserListResponse,
)
from app.services.user_service import UserService

logger = logging.getLogger("app.api.routes.admin")

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=UserListResponse)
async def list_users(
    _admin_key: str = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """List all registered users."""
    users = user_service.list_users()
    logger.info("Admin listed all users (count=%d)", len(users))
    return UserListResponse(
        users=[
            UserDetailResponse(
                id=u.id,
                name=u.name,
                email=u.email,
                status=u.status.value,
                created_at=u.created_at,
                last_active_at=u.last_active_at,
                request_count=u.request_count,
            )
            for u in users
        ],
        total=len(users),
    )


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: str,
    _admin_key: str = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserDetailResponse:
    """Get details for a specific user."""
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")
    return UserDetailResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        status=user.status.value,
        created_at=user.created_at,
        last_active_at=user.last_active_at,
        request_count=user.request_count,
    )


@router.post("/users/{user_id}/disable", response_model=UserDetailResponse)
async def disable_user(
    user_id: str,
    _admin_key: str = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserDetailResponse:
    """Disable a user account. Their API key immediately stops working."""
    user = user_service.disable_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")
    logger.info("Admin disabled user: id=%s email=%s", user.id, user.email)
    return UserDetailResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        status=user.status.value,
        created_at=user.created_at,
        last_active_at=user.last_active_at,
        request_count=user.request_count,
    )


@router.post("/users/{user_id}/enable", response_model=UserDetailResponse)
async def enable_user(
    user_id: str,
    _admin_key: str = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserDetailResponse:
    """Re-enable a previously disabled user account."""
    user = user_service.enable_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")
    logger.info("Admin enabled user: id=%s email=%s", user.id, user.email)
    return UserDetailResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        status=user.status.value,
        created_at=user.created_at,
        last_active_at=user.last_active_at,
        request_count=user.request_count,
    )


@router.post("/users/{user_id}/regenerate-key", response_model=AdminKeyRegenerateResponse)
async def regenerate_key(
    user_id: str,
    _admin_key: str = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
) -> AdminKeyRegenerateResponse:
    """Regenerate a user's API key. The old key is immediately invalidated."""
    new_key = user_service.regenerate_api_key(user_id)
    if new_key is None:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")
    logger.info("Admin regenerated API key for user: id=%s", user_id)
    return AdminKeyRegenerateResponse(id=user_id, new_api_key=new_key)
