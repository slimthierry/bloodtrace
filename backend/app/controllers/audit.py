"""Audit trail endpoints for SIH compliance."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.auth.dependencies import get_current_active_user
from app.auth.rbac import require_roles
from app.models.user_models import User, UserRole
from app.schemas.audit_schemas import AuditLogListResponse
from app.services.audit_service import list_audit_logs

router = APIRouter()


@router.get("", response_model=AuditLogListResponse)
@require_roles([UserRole.ADMIN])
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List audit logs with comprehensive filtering (admin only).

    All system activities are logged for SIH compliance and traceability.
    """
    return await list_audit_logs(
        db, page, page_size, user_id, action, entity_type, entity_id, date_from, date_to
    )
