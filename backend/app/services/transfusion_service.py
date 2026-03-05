"""Transfusion service for request and record management."""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transfusion_models import (
    TransfusionRequest,
    Transfusion,
    RequestStatus,
    ReactionType,
)
from app.models.blood_bag_models import BloodBag, BagStatus
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
from app.auth.exceptions import (
    TransfusionRequestNotFoundException,
    BloodBagNotFoundException,
)


async def get_transfusion_request(
    db: AsyncSession, request_id: int
) -> TransfusionRequest:
    """Get a transfusion request by ID."""
    result = await db.execute(
        select(TransfusionRequest).where(TransfusionRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise TransfusionRequestNotFoundException(request_id)
    return request


async def list_transfusion_requests(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    urgency: Optional[str] = None,
    patient_ipp: Optional[str] = None,
) -> TransfusionRequestListResponse:
    """List transfusion requests with filtering and pagination."""
    query = select(TransfusionRequest)

    if status:
        query = query.where(TransfusionRequest.status == status)
    if urgency:
        query = query.where(TransfusionRequest.urgency == urgency)
    if patient_ipp:
        query = query.where(TransfusionRequest.patient_ipp == patient_ipp)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(TransfusionRequest.created_at.desc())

    result = await db.execute(query)
    requests = result.scalars().all()

    return TransfusionRequestListResponse(
        requests=[TransfusionRequestResponse.model_validate(r) for r in requests],
        total=total,
        page=page,
        page_size=page_size,
    )


async def create_transfusion_request(
    db: AsyncSession,
    request_data: TransfusionRequestCreate,
    doctor_id: int,
) -> TransfusionRequest:
    """Create a new transfusion request."""
    request = TransfusionRequest(
        patient_ipp=request_data.patient_ipp,
        patient_name=request_data.patient_name,
        requesting_doctor_id=doctor_id,
        blood_type_needed=request_data.blood_type_needed,
        rh_needed=request_data.rh_needed,
        component_needed=request_data.component_needed,
        units_needed=request_data.units_needed,
        urgency=request_data.urgency,
        clinical_indication=request_data.clinical_indication,
    )
    db.add(request)
    await db.flush()
    return request


async def update_transfusion_request(
    db: AsyncSession,
    request_id: int,
    request_data: TransfusionRequestUpdate,
) -> TransfusionRequest:
    """Update a transfusion request status."""
    request = await get_transfusion_request(db, request_id)

    update_data = request_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)

    await db.flush()
    return request


async def record_transfusion(
    db: AsyncSession,
    transfusion_data: TransfusionCreate,
    nurse_id: int,
) -> Transfusion:
    """Record a new transfusion being administered."""
    # Verify request exists
    request = await get_transfusion_request(db, transfusion_data.request_id)

    # Verify blood bag exists and is available
    result = await db.execute(
        select(BloodBag).where(BloodBag.id == transfusion_data.blood_bag_id)
    )
    blood_bag = result.scalar_one_or_none()
    if not blood_bag:
        raise BloodBagNotFoundException(transfusion_data.blood_bag_id)

    if blood_bag.status != BagStatus.AVAILABLE.value:
        raise ValueError(
            f"Poche de sang {blood_bag.id} non disponible (statut: {blood_bag.status})"
        )

    # Update blood bag status
    blood_bag.status = BagStatus.TRANSFUSED.value

    # Update request status
    request.status = RequestStatus.IN_PROGRESS.value

    transfusion = Transfusion(
        request_id=transfusion_data.request_id,
        blood_bag_id=transfusion_data.blood_bag_id,
        patient_ipp=transfusion_data.patient_ipp,
        administering_nurse_id=nurse_id,
        started_at=transfusion_data.started_at,
        vital_signs_pre=transfusion_data.vital_signs_pre,
    )
    db.add(transfusion)
    await db.flush()
    return transfusion


async def complete_transfusion(
    db: AsyncSession,
    transfusion_id: int,
    completion_data: TransfusionComplete,
) -> Transfusion:
    """Complete a transfusion and record outcome."""
    result = await db.execute(
        select(Transfusion).where(Transfusion.id == transfusion_id)
    )
    transfusion = result.scalar_one_or_none()
    if not transfusion:
        raise ValueError(f"Transfusion avec l'ID {transfusion_id} non trouvee")

    transfusion.completed_at = completion_data.completed_at
    transfusion.reaction_type = completion_data.reaction_type
    transfusion.reaction_details = completion_data.reaction_details
    transfusion.vital_signs_post = completion_data.vital_signs_post

    # Check if all transfusions for this request are completed
    request = await get_transfusion_request(db, transfusion.request_id)
    all_completed = all(
        t.completed_at is not None for t in request.transfusions
    )
    if all_completed:
        request.status = RequestStatus.COMPLETED.value

    await db.flush()
    return transfusion


async def get_traceability_chain(
    db: AsyncSession, transfusion_id: int
) -> TraceabilityChain:
    """Get the full traceability chain for a transfusion: donor -> bag -> patient."""
    result = await db.execute(
        select(Transfusion).where(Transfusion.id == transfusion_id)
    )
    transfusion = result.scalar_one_or_none()
    if not transfusion:
        raise ValueError(f"Transfusion avec l'ID {transfusion_id} non trouvee")

    blood_bag = transfusion.blood_bag
    donation = blood_bag.donation
    donor = donation.donor
    request = transfusion.request

    return TraceabilityChain(
        donor_ipp=donor.ipp,
        donor_name=donor.full_name,
        donor_blood_group=donor.blood_group_display,
        donation_id=donation.id,
        donation_date=donation.date,
        blood_bag_id=blood_bag.id,
        blood_bag_component=blood_bag.component,
        transfusion_id=transfusion.id,
        patient_ipp=request.patient_ipp,
        patient_name=request.patient_name,
        transfusion_date=transfusion.started_at,
        reaction_type=transfusion.reaction_type,
    )
