"""Audit log schemas for the traceability trail."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Schema for an audit log entry."""

    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: dict
    ip_address: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list."""

    logs: list[AuditLogResponse]
    total: int
    page: int
    page_size: int


class AuditFilter(BaseModel):
    """Filter parameters for audit log queries."""

    user_id: Optional[int] = None
    action: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
