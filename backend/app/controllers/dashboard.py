"""Dashboard endpoints for the main overview page."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.auth.dependencies import get_current_active_user
from app.auth.rbac import require_roles
from app.models.user_models import User, UserRole
from app.schemas.dashboard_schemas import DashboardData
from app.services.dashboard_service import get_dashboard_data

router = APIRouter()


@router.get("", response_model=DashboardData)
@require_roles([UserRole.ADMIN, UserRole.MEDECIN, UserRole.INFIRMIER, UserRole.TECHNICIEN_LABO, UserRole.EFS_AGENT])
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get aggregated dashboard data including stock levels, alerts, and stats."""
    return await get_dashboard_data(db)
