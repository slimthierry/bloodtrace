"""Audit logging utilities for traceability."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_models import AuditLog


async def log_audit(
    db: AsyncSession,
    user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Log an audit entry for traceability.

    Every data access and modification must be logged for SIH compliance.
    """
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
        ip_address=ip_address,
    )
    db.add(audit_entry)
    await db.flush()
    return audit_entry
