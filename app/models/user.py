"""
User Authentication - Pydantic Models

Defines User entity, request/response models, and enums
for the authentication system.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class UserStatus(str, Enum):
    """Account status."""

    ACTIVE = "active"
    DISABLED = "disabled"


class User(BaseModel):
    """Persisted user entity."""

    id: str
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    api_key: str = Field(..., pattern=r"^[a-f0-9]{32}$")
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime
    last_active_at: datetime
    request_count: int = Field(default=0, ge=0)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class UserRegistrationRequest(BaseModel):
    """Input for POST /auth/register."""

    name: str = Field(..., min_length=1, max_length=100)
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class UserRegistrationResponse(BaseModel):
    """Output for POST /auth/register (includes api_key, shown once)."""

    id: str
    name: str
    email: str
    api_key: str
    status: str
    created_at: datetime
    message: str = "Registration successful. Store your API key securely — it will not be shown again."


class UserDetailResponse(BaseModel):
    """Admin view of a user (excludes api_key for security)."""

    id: str
    name: str
    email: str
    status: str
    created_at: datetime
    last_active_at: datetime
    request_count: int


class UserListResponse(BaseModel):
    """Admin list of all users."""

    users: list[UserDetailResponse]
    total: int


class AdminKeyRegenerateResponse(BaseModel):
    """Response when admin regenerates a user's API key."""

    id: str
    new_api_key: str
    message: str = "API key regenerated. Old key is immediately invalid."


class RateLimitInfo(BaseModel):
    """Rate limit state for a single request (not persisted)."""

    limit: int
    remaining: int
    reset_at: datetime
