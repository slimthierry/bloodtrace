"""Authentication schemas for login and token management."""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request with email and password."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    name: str
    role: str


class TokenData(BaseModel):
    """Data embedded in JWT token."""

    sub: str
    role: str
