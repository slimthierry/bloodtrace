"""Inventory service for blood bag management and stock monitoring."""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.blood_bag_models import BloodBag, BagStatus
from app.schemas.blood_bag_schemas import (
    BloodBagCreate,
    BloodBagUpdate,
    BloodBagResponse,
    BloodBagListResponse,
    StockLevel,
    StockSummary,
)
from app.auth.exceptions import BloodBagNotFoundException

# All 8 blood groups
BLOOD_GROUPS = [
    ("A", "+"), ("A", "-"),
    ("B", "+"), ("B", "-"),
    ("AB", "+"), ("AB", "-"),
    ("O", "+"), ("O", "-"),
]


async def get_blood_bag(db: AsyncSession, bag_id: int) -> BloodBag:
    """Get a blood bag by ID."""
    result = await db.execute(select(BloodBag).where(BloodBag.id == bag_id))
    bag = result.scalar_one_or_none()
    if not bag:
        raise BloodBagNotFoundException(bag_id)
    return bag


async def list_blood_bags(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    blood_type: Optional[str] = None,
    rh_factor: Optional[str] = None,
    component: Optional[str] = None,
    status: Optional[str] = None,
    expiring_before: Optional[date] = None,
) -> BloodBagListResponse:
    """List blood bags with filtering and pagination."""
    query = select(BloodBag)

    if blood_type:
        query = query.where(BloodBag.blood_type == blood_type)
    if rh_factor:
        query = query.where(BloodBag.rh_factor == rh_factor)
    if component:
        query = query.where(BloodBag.component == component)
    if status:
        query = query.where(BloodBag.status == status)
    if expiring_before:
        query = query.where(BloodBag.expiry_date <= expiring_before)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(BloodBag.expiry_date.asc())

    result = await db.execute(query)
    bags = result.scalars().all()

    return BloodBagListResponse(
        blood_bags=[BloodBagResponse.model_validate(b) for b in bags],
        total=total,
        page=page,
        page_size=page_size,
    )


async def create_blood_bag(db: AsyncSession, bag_data: BloodBagCreate) -> BloodBag:
    """Create a new blood bag from a donation."""
    bag = BloodBag(
        donation_id=bag_data.donation_id,
        blood_type=bag_data.blood_type,
        rh_factor=bag_data.rh_factor,
        component=bag_data.component,
        volume_ml=bag_data.volume_ml,
        collection_date=bag_data.collection_date,
        expiry_date=bag_data.expiry_date,
        storage_location=bag_data.storage_location,
        storage_temperature=bag_data.storage_temperature,
    )
    db.add(bag)
    await db.flush()
    return bag


async def update_blood_bag(
    db: AsyncSession, bag_id: int, bag_data: BloodBagUpdate
) -> BloodBag:
    """Update a blood bag status or storage info."""
    bag = await get_blood_bag(db, bag_id)

    update_data = bag_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bag, field, value)

    await db.flush()
    return bag


async def get_stock_summary(db: AsyncSession) -> StockSummary:
    """Get stock levels for all 8 blood groups with alerts."""
    today = date.today()
    expiry_threshold = today + timedelta(days=settings.EXPIRY_WARNING_DAYS)
    levels = []
    total_available = 0
    total_expiring = 0
    alerts = []

    for bt, rh in BLOOD_GROUPS:
        blood_group = f"{bt}{rh}"

        # Available count
        available_result = await db.execute(
            select(func.count()).where(
                and_(
                    BloodBag.blood_type == bt,
                    BloodBag.rh_factor == rh,
                    BloodBag.status == BagStatus.AVAILABLE.value,
                    BloodBag.expiry_date >= today,
                )
            )
        )
        available = available_result.scalar() or 0

        # Reserved count
        reserved_result = await db.execute(
            select(func.count()).where(
                and_(
                    BloodBag.blood_type == bt,
                    BloodBag.rh_factor == rh,
                    BloodBag.status.in_([
                        BagStatus.RESERVED.value,
                        BagStatus.CROSSMATCHED.value,
                    ]),
                )
            )
        )
        reserved = reserved_result.scalar() or 0

        # Expiring soon count
        expiring_result = await db.execute(
            select(func.count()).where(
                and_(
                    BloodBag.blood_type == bt,
                    BloodBag.rh_factor == rh,
                    BloodBag.status == BagStatus.AVAILABLE.value,
                    BloodBag.expiry_date >= today,
                    BloodBag.expiry_date <= expiry_threshold,
                )
            )
        )
        expiring = expiring_result.scalar() or 0

        levels.append(
            StockLevel(
                blood_type=bt,
                rh_factor=rh,
                blood_group=blood_group,
                available=available,
                reserved=reserved,
                expiring_soon=expiring,
                total=available + reserved,
            )
        )

        total_available += available
        total_expiring += expiring

        if available < settings.LOW_STOCK_THRESHOLD:
            alerts.append(
                f"Stock critique pour {blood_group}: {available} unites disponibles"
            )

    return StockSummary(
        levels=levels,
        total_available=total_available,
        total_expiring_soon=total_expiring,
        alerts=alerts,
    )


async def get_compatible_bags(
    db: AsyncSession,
    blood_type: str,
    rh_factor: str,
    component: str,
    units_needed: int,
) -> list[BloodBag]:
    """Find compatible available blood bags for a transfusion request."""
    from app.utils.blood_compatibility import get_compatible_donor_types

    compatible_types = get_compatible_donor_types(blood_type, rh_factor)
    today = date.today()

    conditions = [
        BloodBag.status == BagStatus.AVAILABLE.value,
        BloodBag.component == component,
        BloodBag.expiry_date >= today,
    ]

    # Build OR conditions for compatible blood types
    type_conditions = []
    for bt, rh in compatible_types:
        type_conditions.append(
            and_(BloodBag.blood_type == bt, BloodBag.rh_factor == rh)
        )

    if type_conditions:
        from sqlalchemy import or_
        conditions.append(or_(*type_conditions))

    query = (
        select(BloodBag)
        .where(and_(*conditions))
        .order_by(BloodBag.expiry_date.asc())  # FEFO: First Expiry, First Out
        .limit(units_needed)
    )

    result = await db.execute(query)
    return list(result.scalars().all())
