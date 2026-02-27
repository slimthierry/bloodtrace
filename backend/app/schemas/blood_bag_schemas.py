"""Blood bag schemas for inventory management."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class BloodBagCreate(BaseModel):
    """Schema for creating a blood bag from a donation."""

    donation_id: int
    blood_type: str
    rh_factor: str
    component: str
    volume_ml: int
    collection_date: date
    expiry_date: date
    storage_location: Optional[str] = None
    storage_temperature: Optional[float] = None


class BloodBagUpdate(BaseModel):
    """Schema for updating a blood bag."""

    status: Optional[str] = None
    storage_location: Optional[str] = None
    storage_temperature: Optional[float] = None


class BloodBagResponse(BaseModel):
    """Schema for blood bag response."""

    id: int
    donation_id: int
    blood_type: str
    rh_factor: str
    component: str
    volume_ml: int
    collection_date: date
    expiry_date: date
    status: str
    storage_location: Optional[str] = None
    storage_temperature: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BloodBagListResponse(BaseModel):
    """Schema for paginated blood bag list."""

    blood_bags: list[BloodBagResponse]
    total: int
    page: int
    page_size: int


class StockLevel(BaseModel):
    """Stock level for a specific blood type."""

    blood_type: str
    rh_factor: str
    blood_group: str
    available: int
    reserved: int
    expiring_soon: int
    total: int


class StockSummary(BaseModel):
    """Overall stock summary across all blood types."""

    levels: list[StockLevel]
    total_available: int
    total_expiring_soon: int
    alerts: list[str]
