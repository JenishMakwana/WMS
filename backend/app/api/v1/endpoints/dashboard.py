from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import current_active_user
from app.db.session import get_async_session
from app.models.user import User
from app.schemas.dashboard import DashboardKPIs, RecentActivity, StockAlertItem
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis", response_model=DashboardKPIs)
async def get_kpis(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    return await dashboard_service.get_kpis(db, user.id)


@router.get("/activity", response_model=list[RecentActivity])
async def get_recent_activity(
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    return await dashboard_service.get_recent_activity(db, user.id, limit=limit)


@router.get("/alerts", response_model=list[StockAlertItem])
async def get_stock_alerts(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    return await dashboard_service.get_stock_alerts(db, user.id)
