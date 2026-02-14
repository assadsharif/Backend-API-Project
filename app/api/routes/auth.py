"""
User Authentication - Registration Endpoint

POST /auth/register for new user registration.
"""

import logging

from fastapi import APIRouter, Depends

from app.api.dependencies import get_user_service
from app.models.user import (
    UserRegistrationRequest,
    UserRegistrationResponse,
)
from app.services.user_service import UserService

logger = logging.getLogger("app.api.routes.auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRegistrationResponse, status_code=201)
async def register_user(
    body: UserRegistrationRequest,
    user_service: UserService = Depends(get_user_service),
) -> UserRegistrationResponse:
    """Register a new user and receive an API key."""
    user = user_service.create_user(name=body.name, email=body.email)
    logger.info("New user registered: id=%s email=%s", user.id, user.email)
    return UserRegistrationResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        api_key=user.api_key,
        status=user.status.value,
        created_at=user.created_at,
    )
