import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate


class WarehouseService:

    async def get_all(self, db: AsyncSession, user_id: uuid.UUID, active_only: bool = True) -> list[Warehouse]:
        stmt = select(Warehouse).where(Warehouse.user_id == user_id)
        if active_only:
            stmt = stmt.where(Warehouse.is_active == True)
        stmt = stmt.order_by(Warehouse.name)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, warehouse_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Warehouse]:
        result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id, Warehouse.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, short_code: str, user_id: uuid.UUID) -> Optional[Warehouse]:
        result = await db.execute(select(Warehouse).where(Warehouse.short_code == short_code, Warehouse.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, data: WarehouseCreate, user_id: uuid.UUID) -> Warehouse:
        warehouse = Warehouse(**data.model_dump(), user_id=user_id)
        db.add(warehouse)
        await db.commit()
        await db.refresh(warehouse)
        return warehouse

    async def update(self, db: AsyncSession, warehouse: Warehouse, data: WarehouseUpdate) -> Warehouse:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(warehouse, field, value)
        await db.commit()
        await db.refresh(warehouse)
        return warehouse

    async def delete(self, db: AsyncSession, warehouse: Warehouse) -> None:
        warehouse.is_active = False
        await db.commit()


warehouse_service = WarehouseService()
