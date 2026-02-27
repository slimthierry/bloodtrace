"""Donation service for blood collection management."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.donation_models import Donation
from app.models.donor_models import Donor
from app.schemas.donation_schemas import (
    DonationCreate,
    DonationUpdate,
    DonationResponse,
    DonationListResponse,
)
from app.core.exceptions import DonorNotFoundException, DonorIneligibleException


async def get_donation(db: AsyncSession, donation_id: int) -> Donation:
    """Get a donation by ID."""
    result = await db.execute(select(Donation).where(Donation.id == donation_id))
    donation = result.scalar_one_or_none()
    if not donation:
        raise ValueError(f"Don avec l'ID {donation_id} non trouve")
    return donation


async def list_donations(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    donor_id: Optional[int] = None,
    screening_status: Optional[str] = None,
) -> DonationListResponse:
    """List donations with filtering and pagination."""
    query = select(Donation)

    if donor_id:
        query = query.where(Donation.donor_id == donor_id)
    if screening_status:
        query = query.where(Donation.screening_status == screening_status)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Donation.date.desc())

    result = await db.execute(query)
    donations = result.scalars().all()

    return DonationListResponse(
        donations=[DonationResponse.model_validate(d) for d in donations],
        total=total,
        page=page,
        page_size=page_size,
    )


async def create_donation(
    db: AsyncSession, donation_data: DonationCreate, collector_id: int
) -> Donation:
    """Record a new blood donation."""
    # Verify donor exists and is eligible
    result = await db.execute(
        select(Donor).where(Donor.id == donation_data.donor_id)
    )
    donor = result.scalar_one_or_none()
    if not donor:
        raise DonorNotFoundException(donation_data.donor_id)

    if donor.eligibility_status != "eligible":
        raise DonorIneligibleException(
            f"Statut: {donor.eligibility_status}, Raison: {donor.deferral_reason or 'Non specifie'}"
        )

    donation = Donation(
        donor_id=donation_data.donor_id,
        date=donation_data.date,
        volume_ml=donation_data.volume_ml,
        collection_site=donation_data.collection_site,
        collector_id=collector_id,
        notes=donation_data.notes,
    )
    db.add(donation)

    # Update donor stats
    donor.last_donation_date = donation_data.date.date()
    donor.donation_count += 1

    await db.flush()
    return donation


async def update_donation(
    db: AsyncSession, donation_id: int, donation_data: DonationUpdate
) -> Donation:
    """Update a donation record (e.g., screening status)."""
    donation = await get_donation(db, donation_id)

    update_data = donation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(donation, field, value)

    await db.flush()
    return donation
