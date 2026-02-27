"""Audit service for querying the audit trail."""

from typing import Optional
from datetime import datetime

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_models import AuditLog
from app.schemas.audit_schemas import AuditLogResponse, AuditLogListResponse


async def list_audit_logs(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> AuditLogListResponse:
    """List audit logs with comprehensive filtering."""
    query = select(AuditLog)

    conditions = []
    if user_id:
        conditions.append(AuditLog.user_id == user_id)
    if action:
        conditions.append(AuditLog.action == action)
    if entity_type:
        conditions.append(AuditLog.entity_type == entity_type)
    if entity_id:
        conditions.append(AuditLog.entity_id == entity_id)
    if date_from:
        conditions.append(AuditLog.timestamp >= date_from)
    if date_to:
        conditions.append(AuditLog.timestamp <= date_to)

    if conditions:
        query = query.where(and_(*conditions))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(AuditLog.timestamp.desc())

    result = await db.execute(query)
    logs = result.scalars().all()

    return AuditLogListResponse(
        logs=[
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                user_name=log.user.name if log.user else None,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                details=log.details,
                ip_address=log.ip_address,
                timestamp=log.timestamp,
            )
            for log in logs
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
