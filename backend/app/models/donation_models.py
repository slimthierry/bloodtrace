"""Donation model for blood collection tracking."""

import enum
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ScreeningStatus(str, enum.Enum):
    """Screening status for donated blood."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class Donation(Base, TimestampMixin):
    """Blood donation record linked to a donor and collected by staff."""

    __tablename__ = "donations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    donor_id: Mapped[int] = mapped_column(
        ForeignKey("donors.id"), nullable=False, index=True
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    volume_ml: Mapped[int] = mapped_column(Integer, nullable=False)
    collection_site: Mapped[str] = mapped_column(String(255), nullable=False)
    collector_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False,
        comment="User who collected the donation"
    )
    screening_status: Mapped[str] = mapped_column(
        Enum(
            ScreeningStatus,
            name="screening_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=ScreeningStatus.PENDING.value,
        nullable=False,
    )
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    donor = relationship("Donor", back_populates="donations", lazy="selectin")
    collector = relationship("User", lazy="selectin")
    blood_bags = relationship("BloodBag", back_populates="donation", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Donation(id={self.id}, donor_id={self.donor_id}, date='{self.date}')>"
