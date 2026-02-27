"""Donor schemas for blood donor registry management."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class DonorCreate(BaseModel):
    """Schema for registering a new donor."""

    ipp: str
    first_name: str
    last_name: str
    date_of_birth: date
    blood_type: str
    rh_factor: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class DonorUpdate(BaseModel):
    """Schema for updating a donor."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    eligibility_status: Optional[str] = None
    deferral_reason: Optional[str] = None
    deferral_until: Optional[date] = None


class DonorResponse(BaseModel):
    """Schema for donor response."""

    id: int
    ipp: str
    first_name: str
    last_name: str
    date_of_birth: date
    blood_type: str
    rh_factor: str
    last_donation_date: Optional[date] = None
    eligibility_status: str
    deferral_reason: Optional[str] = None
    deferral_until: Optional[date] = None
    donation_count: int
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DonorListResponse(BaseModel):
    """Schema for paginated donor list."""

    donors: list[DonorResponse]
    total: int
    page: int
    page_size: int
