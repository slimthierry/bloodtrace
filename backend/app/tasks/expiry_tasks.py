"""Background tasks for monitoring blood bag expiry dates."""

from datetime import date, timedelta

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.blood_bag_models import BloodBag, BagStatus
from app.services.webhook_service import emit_expiring_blood_alert


async def check_expired_bags(db: AsyncSession) -> int:
    """Mark all expired blood bags and update their status.

    Returns the number of bags marked as expired.
    """
    today = date.today()

    result = await db.execute(
        update(BloodBag)
        .where(
            and_(
                BloodBag.expiry_date < today,
                BloodBag.status == BagStatus.AVAILABLE.value,
            )
        )
        .values(status=BagStatus.EXPIRED.value)
        .returning(BloodBag.id)
    )

    expired_ids = result.scalars().all()
    await db.commit()
    return len(expired_ids)


async def check_expiring_soon(db: AsyncSession) -> int:
    """Check for blood bags expiring within the warning period and send alerts.

    Returns the number of alerts sent.
    """
    today = date.today()
    threshold = today + timedelta(days=settings.EXPIRY_WARNING_DAYS)

    result = await db.execute(
        select(BloodBag).where(
            and_(
                BloodBag.status == BagStatus.AVAILABLE.value,
                BloodBag.expiry_date >= today,
                BloodBag.expiry_date <= threshold,
            )
        )
    )

    expiring_bags = result.scalars().all()
    alert_count = 0

    for bag in expiring_bags:
        days_remaining = (bag.expiry_date - today).days
        await emit_expiring_blood_alert(
            blood_bag_id=bag.id,
            blood_group=f"{bag.blood_type}{bag.rh_factor}",
            expiry_date=bag.expiry_date.isoformat(),
            days_remaining=days_remaining,
        )
        alert_count += 1

    return alert_count
