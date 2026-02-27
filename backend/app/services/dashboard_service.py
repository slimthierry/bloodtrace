"""Dashboard service for the main overview page aggregation."""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.donor_models import Donor
from app.models.donation_models import Donation
from app.models.blood_bag_models import BloodBag, BagStatus
from app.models.transfusion_models import (
    TransfusionRequest,
    Transfusion,
    RequestStatus,
    ReactionType,
)
from app.schemas.dashboard_schemas import (
    DashboardData,
    DashboardStats,
    ExpiringAlert,
    PendingRequest,
    RecentTransfusion,
)
from app.services.inventory_service import get_stock_summary


async def get_dashboard_data(db: AsyncSession) -> DashboardData:
    """Aggregate all dashboard data in a single call."""
    today = date.today()
    first_of_month = today.replace(day=1)
    expiry_threshold = today + timedelta(days=settings.EXPIRY_WARNING_DAYS)

    # Stock levels
    stock_summary = await get_stock_summary(db)

    # Expiring alerts
    expiring_result = await db.execute(
        select(BloodBag)
        .where(
            and_(
                BloodBag.status == BagStatus.AVAILABLE.value,
                BloodBag.expiry_date >= today,
                BloodBag.expiry_date <= expiry_threshold,
            )
        )
        .order_by(BloodBag.expiry_date.asc())
        .limit(10)
    )
    expiring_bags = expiring_result.scalars().all()
    expiring_alerts = [
        ExpiringAlert(
            blood_bag_id=bag.id,
            blood_group=f"{bag.blood_type}{bag.rh_factor}",
            component=bag.component,
            expiry_date=bag.expiry_date.isoformat(),
            days_remaining=(bag.expiry_date - today).days,
        )
        for bag in expiring_bags
    ]

    # Pending requests
    pending_result = await db.execute(
        select(TransfusionRequest)
        .where(TransfusionRequest.status == RequestStatus.PENDING.value)
        .order_by(TransfusionRequest.created_at.desc())
        .limit(10)
    )
    pending_requests_list = pending_result.scalars().all()
    pending_requests = [
        PendingRequest(
            id=req.id,
            patient_ipp=req.patient_ipp,
            patient_name=req.patient_name,
            blood_group_needed=f"{req.blood_type_needed}{req.rh_needed}",
            component_needed=req.component_needed,
            units_needed=req.units_needed,
            urgency=req.urgency,
            created_at=req.created_at,
        )
        for req in pending_requests_list
    ]

    # Recent transfusions
    recent_result = await db.execute(
        select(Transfusion)
        .order_by(Transfusion.started_at.desc())
        .limit(10)
    )
    recent_transfusions_list = recent_result.scalars().all()
    recent_transfusions = [
        RecentTransfusion(
            id=t.id,
            patient_ipp=t.patient_ipp,
            patient_name=t.request.patient_name if t.request else "N/A",
            blood_group=f"{t.blood_bag.blood_type}{t.blood_bag.rh_factor}" if t.blood_bag else "N/A",
            component=t.blood_bag.component if t.blood_bag else "N/A",
            started_at=t.started_at,
            reaction_type=t.reaction_type,
        )
        for t in recent_transfusions_list
    ]

    # Stats
    stats = await _get_dashboard_stats(db, today, first_of_month)

    return DashboardData(
        stock_levels=stock_summary.levels,
        total_available=stock_summary.total_available,
        expiring_alerts=expiring_alerts,
        pending_requests=pending_requests,
        recent_transfusions=recent_transfusions,
        stats=stats,
    )


async def _get_dashboard_stats(
    db: AsyncSession, today: date, first_of_month: date
) -> DashboardStats:
    """Compute aggregate dashboard statistics."""
    # Total donors
    donors_result = await db.execute(select(func.count(Donor.id)))
    total_donors = donors_result.scalar() or 0

    # Donations this month
    donations_result = await db.execute(
        select(func.count(Donation.id)).where(
            Donation.date >= datetime(
                first_of_month.year,
                first_of_month.month,
                first_of_month.day,
                tzinfo=timezone.utc,
            )
        )
    )
    total_donations_month = donations_result.scalar() or 0

    # Transfusions this month
    transfusions_result = await db.execute(
        select(func.count(Transfusion.id)).where(
            Transfusion.started_at >= datetime(
                first_of_month.year,
                first_of_month.month,
                first_of_month.day,
                tzinfo=timezone.utc,
            )
        )
    )
    total_transfusions_month = transfusions_result.scalar() or 0

    # Available blood bags
    available_result = await db.execute(
        select(func.count(BloodBag.id)).where(
            and_(
                BloodBag.status == BagStatus.AVAILABLE.value,
                BloodBag.expiry_date >= today,
            )
        )
    )
    total_available = available_result.scalar() or 0

    # Pending requests
    pending_result = await db.execute(
        select(func.count(TransfusionRequest.id)).where(
            TransfusionRequest.status == RequestStatus.PENDING.value
        )
    )
    total_pending = pending_result.scalar() or 0

    # Reactions this month
    reactions_result = await db.execute(
        select(func.count(Transfusion.id)).where(
            and_(
                Transfusion.reaction_type != ReactionType.NONE.value,
                Transfusion.started_at >= datetime(
                    first_of_month.year,
                    first_of_month.month,
                    first_of_month.day,
                    tzinfo=timezone.utc,
                ),
            )
        )
    )
    reactions_month = reactions_result.scalar() or 0

    return DashboardStats(
        total_donors=total_donors,
        total_donations_this_month=total_donations_month,
        total_transfusions_this_month=total_transfusions_month,
        total_blood_bags_available=total_available,
        total_pending_requests=total_pending,
        reactions_this_month=reactions_month,
    )
