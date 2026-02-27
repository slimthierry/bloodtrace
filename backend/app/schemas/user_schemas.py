"""User schemas for CRUD operations."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr
    name: str
    password: str
    role: str
    service: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    name: Optional[str] = None
    role: Optional[str] = None
    service: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    email: str
    name: str
    role: str
    service: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Schema for paginated user list."""

    users: list[UserResponse]
    total: int
    page: int
    page_size: int
