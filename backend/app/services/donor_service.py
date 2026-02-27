"""Donor service for blood donor registry management."""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.donor_models import Donor
from app.schemas.donor_schemas import DonorCreate, DonorUpdate, DonorResponse, DonorListResponse
from app.core.exceptions import DonorNotFoundException


async def get_donor(db: AsyncSession, donor_id: int) -> Donor:
    """Get a donor by ID."""
    result = await db.execute(select(Donor).where(Donor.id == donor_id))
    donor = result.scalar_one_or_none()
    if not donor:
        raise DonorNotFoundException(donor_id)
    return donor


async def get_donor_by_ipp(db: AsyncSession, ipp: str) -> Optional[Donor]:
    """Get a donor by IPP (Identifiant Permanent du Patient)."""
    result = await db.execute(select(Donor).where(Donor.ipp == ipp))
    return result.scalar_one_or_none()


async def list_donors(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    blood_type: Optional[str] = None,
    eligibility: Optional[str] = None,
    search: Optional[str] = None,
) -> DonorListResponse:
    """List donors with filtering and pagination."""
    query = select(Donor)

    if blood_type:
        query = query.where(Donor.blood_type == blood_type)
    if eligibility:
        query = query.where(Donor.eligibility_status == eligibility)
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Donor.first_name.ilike(search_filter))
            | (Donor.last_name.ilike(search_filter))
            | (Donor.ipp.ilike(search_filter))
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Donor.created_at.desc())

    result = await db.execute(query)
    donors = result.scalars().all()

    return DonorListResponse(
        donors=[DonorResponse.model_validate(d) for d in donors],
        total=total,
        page=page,
        page_size=page_size,
    )


async def create_donor(db: AsyncSession, donor_data: DonorCreate) -> Donor:
    """Register a new donor."""
    # Check if IPP already exists
    existing = await get_donor_by_ipp(db, donor_data.ipp)
    if existing:
        raise ValueError(f"Un donneur avec l'IPP {donor_data.ipp} existe deja")

    donor = Donor(
        ipp=donor_data.ipp,
        first_name=donor_data.first_name,
        last_name=donor_data.last_name,
        date_of_birth=donor_data.date_of_birth,
        blood_type=donor_data.blood_type,
        rh_factor=donor_data.rh_factor,
        phone=donor_data.phone,
        email=donor_data.email,
    )
    db.add(donor)
    await db.flush()
    return donor


async def update_donor(
    db: AsyncSession, donor_id: int, donor_data: DonorUpdate
) -> Donor:
    """Update an existing donor."""
    donor = await get_donor(db, donor_id)

    update_data = donor_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(donor, field, value)

    await db.flush()
    return donor
