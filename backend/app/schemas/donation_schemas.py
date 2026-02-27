"""Donation schemas for blood collection tracking."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DonationCreate(BaseModel):
    """Schema for recording a new donation."""

    donor_id: int
    date: datetime
    volume_ml: int
    collection_site: str
    notes: Optional[str] = None


class DonationUpdate(BaseModel):
    """Schema for updating a donation record."""

    screening_status: Optional[str] = None
    notes: Optional[str] = None


class DonationResponse(BaseModel):
    """Schema for donation response."""

    id: int
    donor_id: int
    date: datetime
    volume_ml: int
    collection_site: str
    collector_id: int
    screening_status: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DonationListResponse(BaseModel):
    """Schema for paginated donation list."""

    donations: list[DonationResponse]
    total: int
    page: int
    page_size: int
