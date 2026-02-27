"""Background tasks for monitoring blood stock levels."""

from datetime import date

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.blood_bag_models import BloodBag, BagStatus
from app.services.inventory_service import BLOOD_GROUPS
from app.services.webhook_service import emit_low_stock_alert


async def check_stock_levels(db: AsyncSession) -> int:
    """Check stock levels for all blood groups and send low stock alerts.

    Returns the number of alerts sent.
    """
    today = date.today()
    alert_count = 0

    for bt, rh in BLOOD_GROUPS:
        blood_group = f"{bt}{rh}"

        result = await db.execute(
            select(func.count()).where(
                and_(
                    BloodBag.blood_type == bt,
                    BloodBag.rh_factor == rh,
                    BloodBag.status == BagStatus.AVAILABLE.value,
                    BloodBag.expiry_date >= today,
                )
            )
        )
        available_count = result.scalar() or 0

        if available_count < settings.LOW_STOCK_THRESHOLD:
            await emit_low_stock_alert(
                blood_group=blood_group,
                available_count=available_count,
                threshold=settings.LOW_STOCK_THRESHOLD,
            )
            alert_count += 1

    return alert_count
