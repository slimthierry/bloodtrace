"""Blood bag inventory management endpoints."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.auth.dependencies import get_current_active_user
from app.auth.rbac import require_roles
from app.auth.audit import log_audit
from app.models.user_models import User, UserRole
from app.schemas.blood_bag_schemas import (
    BloodBagCreate,
    BloodBagUpdate,
    BloodBagResponse,
    BloodBagListResponse,
    StockSummary,
)
from app.services.inventory_service import (
    get_blood_bag,
    list_blood_bags,
    create_blood_bag,
    update_blood_bag,
    get_stock_summary,
    get_compatible_bags,
)
from app.services.compatibility_service import check_compatibility, get_compatibility_matrix

router = APIRouter()


@router.get("", response_model=BloodBagListResponse)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.TECHNICIEN_LABO, UserRole.EFS_AGENT])
async def get_blood_bags(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    blood_type: Optional[str] = None,
    rh_factor: Optional[str] = None,
    component: Optional[str] = None,
    status: Optional[str] = None,
    expiring_before: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List blood bags with comprehensive filtering."""
    return await list_blood_bags(
        db, page, page_size, blood_type, rh_factor, component, status, expiring_before
    )


@router.get("/stock", response_model=StockSummary)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.TECHNICIEN_LABO, UserRole.EFS_AGENT])
async def get_stock_levels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current stock levels for all 8 blood groups."""
    return await get_stock_summary(db)


@router.get("/compatibility")
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.TECHNICIEN_LABO])
async def get_compatibility(
    current_user: User = Depends(get_current_active_user),
):
    """Get the full ABO+Rh compatibility matrix."""
    return get_compatibility_matrix()


@router.get("/compatibility/check")
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.TECHNICIEN_LABO])
async def check_blood_compatibility(
    donor_type: str,
    donor_rh: str,
    recipient_type: str,
    recipient_rh: str,
    component: str = "packed_rbc",
    current_user: User = Depends(get_current_active_user),
):
    """Check compatibility between specific donor and recipient blood types."""
    return check_compatibility(
        donor_type, donor_rh, recipient_type, recipient_rh, component
    )


@router.get("/match")
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.TECHNICIEN_LABO])
async def find_compatible_bags(
    blood_type: str,
    rh_factor: str,
    component: str,
    units_needed: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Find compatible available blood bags for a transfusion."""
    bags = await get_compatible_bags(db, blood_type, rh_factor, component, units_needed)
    return {
        "requested": {
            "blood_type": blood_type,
            "rh_factor": rh_factor,
            "component": component,
            "units_needed": units_needed,
        },
        "matches": [BloodBagResponse.model_validate(b) for b in bags],
        "found": len(bags),
        "sufficient": len(bags) >= units_needed,
    }


@router.get("/{bag_id}", response_model=BloodBagResponse)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.TECHNICIEN_LABO, UserRole.EFS_AGENT])
async def get_blood_bag_by_id(
    bag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a blood bag by ID."""
    bag = await get_blood_bag(db, bag_id)
    return BloodBagResponse.model_validate(bag)


@router.post("", response_model=BloodBagResponse, status_code=201)
@require_roles([UserRole.ADMIN, UserRole.TECHNICIEN_LABO, UserRole.EFS_AGENT])
async def create_new_blood_bag(
    bag_data: BloodBagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new blood bag from a donation."""
    bag = await create_blood_bag(db, bag_data)
    await log_audit(
        db, current_user.id, "create", "blood_bag", str(bag.id),
        {
            "blood_group": f"{bag.blood_type}{bag.rh_factor}",
            "component": bag.component,
            "donation_id": bag.donation_id,
        },
    )
    return BloodBagResponse.model_validate(bag)


@router.put("/{bag_id}", response_model=BloodBagResponse)
@require_roles([UserRole.ADMIN, UserRole.TECHNICIEN_LABO, UserRole.EFS_AGENT])
async def update_existing_blood_bag(
    bag_id: int,
    bag_data: BloodBagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a blood bag status or storage information."""
    bag = await update_blood_bag(db, bag_id, bag_data)
    await log_audit(
        db, current_user.id, "update", "blood_bag", str(bag.id),
        {"updated_fields": list(bag_data.model_dump(exclude_unset=True).keys())},
    )
    return BloodBagResponse.model_validate(bag)
