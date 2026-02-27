"""Transfusion request and record management endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.rbac import require_roles
from app.core.audit import log_audit
from app.models.user_models import User, UserRole
from app.schemas.transfusion_schemas import (
    TransfusionRequestCreate,
    TransfusionRequestUpdate,
    TransfusionRequestResponse,
    TransfusionRequestListResponse,
    TransfusionCreate,
    TransfusionComplete,
    TransfusionResponse,
    TraceabilityChain,
)
from app.services.transfusion_service import (
    list_transfusion_requests,
    get_transfusion_request,
    create_transfusion_request,
    update_transfusion_request,
    record_transfusion,
    complete_transfusion,
    get_traceability_chain,
)
from app.services.webhook_service import emit_transfusion_reaction_alert

router = APIRouter()


# --- Transfusion Requests ---

@router.get("/requests", response_model=TransfusionRequestListResponse)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.INFIRMIER, UserRole.TECHNICIEN_LABO])
async def get_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    urgency: Optional[str] = None,
    patient_ipp: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List transfusion requests with filtering."""
    return await list_transfusion_requests(
        db, page, page_size, status, urgency, patient_ipp
    )


@router.get("/requests/{request_id}", response_model=TransfusionRequestResponse)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.INFIRMIER, UserRole.TECHNICIEN_LABO])
async def get_request_by_id(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a transfusion request by ID."""
    request = await get_transfusion_request(db, request_id)
    return TransfusionRequestResponse.model_validate(request)


@router.post("/requests", response_model=TransfusionRequestResponse, status_code=201)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN])
async def create_request(
    request_data: TransfusionRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new transfusion request (physician only)."""
    request = await create_transfusion_request(db, request_data, current_user.id)
    await log_audit(
        db, current_user.id, "create", "transfusion_request", str(request.id),
        {
            "patient_ipp": request.patient_ipp,
            "blood_group": f"{request.blood_type_needed}{request.rh_needed}",
            "urgency": request.urgency,
        },
    )
    return TransfusionRequestResponse.model_validate(request)


@router.put("/requests/{request_id}", response_model=TransfusionRequestResponse)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.TECHNICIEN_LABO])
async def update_request(
    request_id: int,
    request_data: TransfusionRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a transfusion request (approve/reject/cancel)."""
    request = await update_transfusion_request(db, request_id, request_data)
    await log_audit(
        db, current_user.id, "update", "transfusion_request", str(request.id),
        {"updated_fields": list(request_data.model_dump(exclude_unset=True).keys())},
    )
    return TransfusionRequestResponse.model_validate(request)


# --- Transfusions ---

@router.post("", response_model=TransfusionResponse, status_code=201)
@require_roles([UserRole.ADMIN, UserRole.INFIRMIER])
async def start_transfusion(
    transfusion_data: TransfusionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record the start of a transfusion (nurse only)."""
    try:
        transfusion = await record_transfusion(db, transfusion_data, current_user.id)
        await log_audit(
            db, current_user.id, "create", "transfusion", str(transfusion.id),
            {
                "patient_ipp": transfusion.patient_ipp,
                "blood_bag_id": transfusion.blood_bag_id,
                "request_id": transfusion.request_id,
            },
        )
        return TransfusionResponse.model_validate(transfusion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{transfusion_id}/complete", response_model=TransfusionResponse)
@require_roles([UserRole.ADMIN, UserRole.INFIRMIER])
async def finish_transfusion(
    transfusion_id: int,
    completion_data: TransfusionComplete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record the completion of a transfusion with outcome."""
    try:
        transfusion = await complete_transfusion(db, transfusion_id, completion_data)
        await log_audit(
            db, current_user.id, "update", "transfusion", str(transfusion.id),
            {
                "reaction_type": transfusion.reaction_type,
                "completed": True,
            },
        )

        # Emit webhook if there was a reaction
        if completion_data.reaction_type != "none":
            await emit_transfusion_reaction_alert(
                transfusion_id=transfusion.id,
                patient_ipp=transfusion.patient_ipp,
                reaction_type=completion_data.reaction_type,
                reaction_details=completion_data.reaction_details,
            )

        return TransfusionResponse.model_validate(transfusion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{transfusion_id}/trace", response_model=TraceabilityChain)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.INFIRMIER, UserRole.TECHNICIEN_LABO])
async def get_transfusion_trace(
    transfusion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get the full traceability chain for a transfusion: donor -> bag -> patient."""
    try:
        return await get_traceability_chain(db, transfusion_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
