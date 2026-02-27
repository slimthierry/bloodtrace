"""Audit log model for full traceability of all system operations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AuditLog(Base):
    """Audit log entry for SIH compliance.

    Every data access and modification is logged with the user, action,
    entity, and details for complete traceability.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True,
        comment="create, read, update, delete"
    )
    entity_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    entity_id: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True
    )
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    user = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, user_id={self.user_id}, "
            f"action='{self.action}', entity='{self.entity_type}')>"
        )
