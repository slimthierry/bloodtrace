"""Authentication service for login and user management."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import verify_password, get_password_hash, create_access_token
from app.models.user_models import User
from app.schemas.auth_schemas import LoginRequest, TokenResponse
from app.schemas.user_schemas import UserCreate


async def authenticate_user(
    db: AsyncSession, login_data: LoginRequest
) -> TokenResponse | None:
    """Authenticate a user and return a JWT token."""
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.flush()

    # Create token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
    )


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user account."""
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("Un utilisateur avec cet email existe deja")

    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        service=user_data.service,
    )
    db.add(user)
    await db.flush()
    return user
