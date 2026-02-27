"""Dashboard schemas for the main overview page."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.blood_bag_schemas import StockLevel


class ExpiringAlert(BaseModel):
    """Alert for blood bags nearing expiry."""

    blood_bag_id: int
    blood_group: str
    component: str
    expiry_date: str
    days_remaining: int


class PendingRequest(BaseModel):
    """Summary of a pending transfusion request."""

    id: int
    patient_ipp: str
    patient_name: str
    blood_group_needed: str
    component_needed: str
    units_needed: int
    urgency: str
    created_at: datetime


class RecentTransfusion(BaseModel):
    """Summary of a recent transfusion."""

    id: int
    patient_ipp: str
    patient_name: str
    blood_group: str
    component: str
    started_at: datetime
    reaction_type: str


class DashboardData(BaseModel):
    """Complete dashboard data combining all widgets."""

    stock_levels: list[StockLevel]
    total_available: int
    expiring_alerts: list[ExpiringAlert]
    pending_requests: list[PendingRequest]
    recent_transfusions: list[RecentTransfusion]
    stats: "DashboardStats"


class DashboardStats(BaseModel):
    """Aggregate statistics for the dashboard."""

    total_donors: int
    total_donations_this_month: int
    total_transfusions_this_month: int
    total_blood_bags_available: int
    total_pending_requests: int
    reactions_this_month: int
