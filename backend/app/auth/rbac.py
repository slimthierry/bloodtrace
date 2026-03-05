"""Role-Based Access Control (RBAC) decorator for endpoint authorization."""

from functools import wraps
from typing import List

from fastapi import HTTPException, status

from app.models.user_models import UserRole


def require_roles(allowed_roles: List[UserRole]):
    """Decorator to restrict endpoint access to specific roles.

    Usage:
        @router.get("/protected")
        @require_roles([UserRole.ADMIN, UserRole.MEDECIN])
        async def protected_endpoint(current_user: User = Depends(get_current_active_user)):
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentification requise",
                )

            if current_user.role not in [role.value for role in allowed_roles]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role requis: {', '.join([r.value for r in allowed_roles])}. "
                    f"Votre role: {current_user.role}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
