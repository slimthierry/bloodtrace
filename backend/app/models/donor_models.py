"""Donor model for blood donor registry management."""

import enum
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class BloodType(str, enum.Enum):
    """ABO blood group system."""

    A = "A"
    B = "B"
    AB = "AB"
    O = "O"


class RhFactor(str, enum.Enum):
    """Rh factor."""

    POSITIVE = "+"
    NEGATIVE = "-"


class EligibilityStatus(str, enum.Enum):
    """Donor eligibility status."""

    ELIGIBLE = "eligible"
    TEMPORARY_DEFERRAL = "temporary_deferral"
    PERMANENT_DEFERRAL = "permanent_deferral"


class Donor(Base, TimestampMixin):
    """Blood donor with identification via IPP (Identifiant Permanent du Patient)."""

    __tablename__ = "donors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ipp: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False,
        comment="Identifiant Permanent du Patient"
    )
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    blood_type: Mapped[str] = mapped_column(
        Enum(BloodType, name="blood_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    rh_factor: Mapped[str] = mapped_column(
        Enum(RhFactor, name="rh_factor", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    last_donation_date: Mapped[date] = mapped_column(Date, nullable=True)
    eligibility_status: Mapped[str] = mapped_column(
        Enum(
            EligibilityStatus,
            name="eligibility_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=EligibilityStatus.ELIGIBLE.value,
        nullable=False,
    )
    deferral_reason: Mapped[str] = mapped_column(String(500), nullable=True)
    deferral_until: Mapped[date] = mapped_column(Date, nullable=True)
    donation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)

    # Relationships
    donations = relationship("Donation", back_populates="donor", lazy="selectin")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def blood_group_display(self) -> str:
        return f"{self.blood_type}{self.rh_factor}"

    def __repr__(self) -> str:
        return f"<Donor(id={self.id}, ipp='{self.ipp}', name='{self.full_name}', blood='{self.blood_group_display}')>"
