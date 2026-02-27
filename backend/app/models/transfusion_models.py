"""Transfusion request and record models for complete traceability."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Urgency(str, enum.Enum):
    """Transfusion request urgency levels."""

    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    MASSIVE = "massive"


class RequestStatus(str, enum.Enum):
    """Transfusion request lifecycle status."""

    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReactionType(str, enum.Enum):
    """Transfusion reaction severity levels."""

    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class TransfusionRequest(Base, TimestampMixin):
    """Transfusion request from a prescribing physician."""

    __tablename__ = "transfusion_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_ipp: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
        comment="Identifiant Permanent du Patient"
    )
    patient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    requesting_doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    blood_type_needed: Mapped[str] = mapped_column(String(2), nullable=False)
    rh_needed: Mapped[str] = mapped_column(String(1), nullable=False)
    component_needed: Mapped[str] = mapped_column(String(50), nullable=False)
    units_needed: Mapped[int] = mapped_column(Integer, nullable=False)
    urgency: Mapped[str] = mapped_column(
        Enum(
            Urgency,
            name="urgency",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=Urgency.ROUTINE.value,
        nullable=False,
    )
    clinical_indication: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            RequestStatus,
            name="request_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=RequestStatus.PENDING.value,
        nullable=False,
        index=True,
    )

    # Relationships
    requesting_doctor = relationship("User", lazy="selectin")
    transfusions = relationship("Transfusion", back_populates="request", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<TransfusionRequest(id={self.id}, patient_ipp='{self.patient_ipp}', "
            f"urgency='{self.urgency}', status='{self.status}')>"
        )


class Transfusion(Base, TimestampMixin):
    """Transfusion record with full traceability chain: donor -> bag -> patient."""

    __tablename__ = "transfusions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("transfusion_requests.id"), nullable=False, index=True
    )
    blood_bag_id: Mapped[int] = mapped_column(
        ForeignKey("blood_bags.id"), nullable=False, index=True
    )
    patient_ipp: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
        comment="Identifiant Permanent du Patient"
    )
    administering_nurse_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reaction_type: Mapped[str] = mapped_column(
        Enum(
            ReactionType,
            name="reaction_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=ReactionType.NONE.value,
        nullable=False,
    )
    reaction_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vital_signs_pre: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    vital_signs_post: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    request = relationship("TransfusionRequest", back_populates="transfusions", lazy="selectin")
    blood_bag = relationship("BloodBag", lazy="selectin")
    administering_nurse = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<Transfusion(id={self.id}, request_id={self.request_id}, "
            f"patient_ipp='{self.patient_ipp}', reaction='{self.reaction_type}')>"
        )
