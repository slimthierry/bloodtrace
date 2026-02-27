"""Donation management endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.rbac import require_roles
from app.core.audit import log_audit
from app.models.user_models import User, UserRole
from app.schemas.donation_schemas import (
    DonationCreate,
    DonationUpdate,
    DonationResponse,
    DonationListResponse,
)
from app.services.donation_service import (
    get_donation,
    list_donations,
    create_donation,
    update_donation,
)

router = APIRouter()


@router.get("", response_model=DonationListResponse)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.TECHNICIEN_LABO, UserRole.EFS_AGENT])
async def get_donations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    donor_id: Optional[int] = None,
    screening_status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all donations with filtering and pagination."""
    return await list_donations(db, page, page_size, donor_id, screening_status)


@router.get("/{donation_id}", response_model=DonationResponse)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.TECHNICIEN_LABO, UserRole.EFS_AGENT])
async def get_donation_by_id(
    donation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a donation by ID."""
    donation = await get_donation(db, donation_id)
    return DonationResponse.model_validate(donation)


@router.post("", response_model=DonationResponse, status_code=201)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.INFIRMIER, UserRole.EFS_AGENT])
async def create_new_donation(
    donation_data: DonationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record a new blood donation."""
    try:
        donation = await create_donation(db, donation_data, current_user.id)
        await log_audit(
            db, current_user.id, "create", "donation", str(donation.id),
            {"donor_id": donation.donor_id, "volume_ml": donation.volume_ml},
        )
        return DonationResponse.model_validate(donation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{donation_id}", response_model=DonationResponse)
@require_roles([UserRole.ADMIN, UserRole.TECHNICIEN_LABO])
async def update_existing_donation(
    donation_id: int,
    donation_data: DonationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a donation record (e.g., screening status)."""
    donation = await update_donation(db, donation_id, donation_data)
    await log_audit(
        db, current_user.id, "update", "donation", str(donation.id),
        {"updated_fields": list(donation_data.model_dump(exclude_unset=True).keys())},
    )
    return DonationResponse.model_validate(donation)
