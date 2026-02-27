"""Transfusion schemas for request and record management."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TransfusionRequestCreate(BaseModel):
    """Schema for creating a transfusion request."""

    patient_ipp: str
    patient_name: str
    blood_type_needed: str
    rh_needed: str
    component_needed: str
    units_needed: int
    urgency: str = "routine"
    clinical_indication: str


class TransfusionRequestUpdate(BaseModel):
    """Schema for updating a transfusion request."""

    status: Optional[str] = None
    units_needed: Optional[int] = None
    urgency: Optional[str] = None


class TransfusionRequestResponse(BaseModel):
    """Schema for transfusion request response."""

    id: int
    patient_ipp: str
    patient_name: str
    requesting_doctor_id: int
    blood_type_needed: str
    rh_needed: str
    component_needed: str
    units_needed: int
    urgency: str
    clinical_indication: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TransfusionRequestListResponse(BaseModel):
    """Schema for paginated transfusion request list."""

    requests: list[TransfusionRequestResponse]
    total: int
    page: int
    page_size: int


class TransfusionCreate(BaseModel):
    """Schema for recording a transfusion."""

    request_id: int
    blood_bag_id: int
    patient_ipp: str
    started_at: datetime
    vital_signs_pre: Optional[dict] = None


class TransfusionComplete(BaseModel):
    """Schema for completing a transfusion."""

    completed_at: datetime
    reaction_type: str = "none"
    reaction_details: Optional[str] = None
    vital_signs_post: Optional[dict] = None


class TransfusionResponse(BaseModel):
    """Schema for transfusion response."""

    id: int
    request_id: int
    blood_bag_id: int
    patient_ipp: str
    administering_nurse_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    reaction_type: str
    reaction_details: Optional[str] = None
    vital_signs_pre: Optional[dict] = None
    vital_signs_post: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TraceabilityChain(BaseModel):
    """Full traceability chain: donor -> donation -> bag -> transfusion -> patient."""

    donor_ipp: str
    donor_name: str
    donor_blood_group: str
    donation_id: int
    donation_date: datetime
    blood_bag_id: int
    blood_bag_component: str
    transfusion_id: int
    patient_ipp: str
    patient_name: str
    transfusion_date: datetime
    reaction_type: str
