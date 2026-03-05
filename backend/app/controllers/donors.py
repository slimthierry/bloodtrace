"""Donor management endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.auth.dependencies import get_current_active_user
from app.auth.rbac import require_roles
from app.auth.audit import log_audit
from app.models.user_models import User, UserRole
from app.schemas.donor_schemas import (
    DonorCreate,
    DonorUpdate,
    DonorResponse,
    DonorListResponse,
)
from app.services.donor_service import (
    get_donor,
    get_donor_by_ipp,
    list_donors,
    create_donor,
    update_donor,
)

router = APIRouter()


@router.get("", response_model=DonorListResponse)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.INFIRMIER, UserRole.TECHNICIEN_LABO, UserRole.EFS_AGENT])
async def get_donors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    blood_type: Optional[str] = None,
    eligibility: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all donors with filtering and pagination."""
    return await list_donors(db, page, page_size, blood_type, eligibility, search)


@router.get("/{donor_id}", response_model=DonorResponse)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.INFIRMIER, UserRole.TECHNICIEN_LABO, UserRole.EFS_AGENT])
async def get_donor_by_id(
    donor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a donor by ID."""
    donor = await get_donor(db, donor_id)
    return DonorResponse.model_validate(donor)


@router.get("/ipp/{ipp}", response_model=DonorResponse)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.INFIRMIER, UserRole.TECHNICIEN_LABO, UserRole.EFS_AGENT])
async def get_donor_by_ipp_endpoint(
    ipp: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a donor by IPP (Identifiant Permanent du Patient)."""
    donor = await get_donor_by_ipp(db, ipp)
    if not donor:
        raise HTTPException(status_code=404, detail=f"Donneur avec IPP {ipp} non trouve")
    return DonorResponse.model_validate(donor)


@router.post("", response_model=DonorResponse, status_code=201)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.EFS_AGENT])
async def create_new_donor(
    donor_data: DonorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Register a new blood donor."""
    try:
        donor = await create_donor(db, donor_data)
        await log_audit(
            db, current_user.id, "create", "donor", str(donor.id),
            {"ipp": donor.ipp, "blood_group": donor.blood_group_display},
        )
        return DonorResponse.model_validate(donor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{donor_id}", response_model=DonorResponse)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.EFS_AGENT])
async def update_existing_donor(
    donor_id: int,
    donor_data: DonorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing donor."""
    donor = await update_donor(db, donor_id, donor_data)
    await log_audit(
        db, current_user.id, "update", "donor", str(donor.id),
        {"updated_fields": list(donor_data.model_dump(exclude_unset=True).keys())},
    )
    return DonorResponse.model_validate(donor)
