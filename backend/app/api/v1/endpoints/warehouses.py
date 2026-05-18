import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import current_active_user
from app.db.session import get_async_session
from app.models.user import User
from app.schemas.warehouse import WarehouseCreate, WarehouseRead, WarehouseUpdate
from app.services.warehouse_service import warehouse_service

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@router.get("/", response_model=list[WarehouseRead])
async def list_warehouses(
    active_only: bool = True,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    return await warehouse_service.get_all(db, user_id=user.id, active_only=active_only)


@router.post("/", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    data: WarehouseCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    existing = await warehouse_service.get_by_code(db, data.short_code, user_id=user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Short code already in use")
    return await warehouse_service.create(db, data, user_id=user.id)


@router.get("/{warehouse_id}", response_model=WarehouseRead)
async def get_warehouse(
    warehouse_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    wh = await warehouse_service.get_by_id(db, warehouse_id, user_id=user.id)
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return wh


@router.patch("/{warehouse_id}", response_model=WarehouseRead)
async def update_warehouse(
    warehouse_id: uuid.UUID,
    data: WarehouseUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    wh = await warehouse_service.get_by_id(db, warehouse_id, user_id=user.id)
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return await warehouse_service.update(db, wh, data)


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_warehouse(
    warehouse_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    wh = await warehouse_service.get_by_id(db, warehouse_id, user_id=user.id)
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    await warehouse_service.delete(db, wh)
