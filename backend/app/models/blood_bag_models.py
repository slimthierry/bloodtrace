"""Blood bag model for inventory management and traceability."""

import enum
from datetime import date, datetime

from sqlalchemy import String, Integer, Float, ForeignKey, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class BloodComponent(str, enum.Enum):
    """Blood product components."""

    WHOLE_BLOOD = "whole_blood"
    PACKED_RBC = "packed_rbc"
    PLASMA = "plasma"
    PLATELETS = "platelets"
    CRYOPRECIPITATE = "cryoprecipitate"


class BagStatus(str, enum.Enum):
    """Blood bag lifecycle status."""

    AVAILABLE = "available"
    RESERVED = "reserved"
    CROSSMATCHED = "crossmatched"
    TRANSFUSED = "transfused"
    EXPIRED = "expired"
    DISCARDED = "discarded"
    QUARANTINE = "quarantine"


class BloodBag(Base, TimestampMixin):
    """Blood bag with full traceability from donation to transfusion."""

    __tablename__ = "blood_bags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    donation_id: Mapped[int] = mapped_column(
        ForeignKey("donations.id"), nullable=False, index=True
    )
    blood_type: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    rh_factor: Mapped[str] = mapped_column(String(1), nullable=False, index=True)
    component: Mapped[str] = mapped_column(
        Enum(
            BloodComponent,
            name="blood_component",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        index=True,
    )
    volume_ml: Mapped[int] = mapped_column(Integer, nullable=False)
    collection_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum(
            BagStatus,
            name="bag_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=BagStatus.AVAILABLE.value,
        nullable=False,
        index=True,
    )
    storage_location: Mapped[str] = mapped_column(String(255), nullable=True)
    storage_temperature: Mapped[float] = mapped_column(Float, nullable=True)

    # Relationships
    donation = relationship("Donation", back_populates="blood_bags", lazy="selectin")

    @property
    def blood_group_display(self) -> str:
        return f"{self.blood_type}{self.rh_factor}"

    @property
    def is_expired(self) -> bool:
        from datetime import date as date_type
        return self.expiry_date < date_type.today()

    def __repr__(self) -> str:
        return (
            f"<BloodBag(id={self.id}, type='{self.blood_group_display}', "
            f"component='{self.component}', status='{self.status}')>"
        )
