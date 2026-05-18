import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate


class LocationService:

    async def get_all(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        warehouse_id: Optional[uuid.UUID] = None,
        active_only: bool = True,
    ) -> list[Location]:
        stmt = (
            select(Location)
            .join(Location.warehouse)
            .options(selectinload(Location.warehouse))
            .where(Location.warehouse.has(user_id=user_id))
        )
        if active_only:
            stmt = stmt.where(Location.is_active == True)
        if warehouse_id:
            stmt = stmt.where(Location.warehouse_id == warehouse_id)
        stmt = stmt.order_by(Location.name)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, location_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Location]:
        result = await db.execute(
            select(Location)
            .join(Location.warehouse)
            .options(selectinload(Location.warehouse))
            .where(Location.id == location_id, Location.warehouse.has(user_id=user_id))
        )
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, data: LocationCreate, user_id: uuid.UUID) -> Location:
        # Verify warehouse ownership
        from app.models.warehouse import Warehouse
        res = await db.execute(select(Warehouse).where(Warehouse.id == data.warehouse_id, Warehouse.user_id == user_id))
        wh = res.scalar_one_or_none()
        if not wh:
            raise ValueError("Warehouse not found")

        location = Location(**data.model_dump())
        db.add(location)
        await db.commit()
        await db.refresh(location)
        return location

    async def update(self, db: AsyncSession, location: Location, data: LocationUpdate) -> Location:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(location, field, value)
        await db.commit()
        await db.refresh(location)
        return location

    async def delete(self, db: AsyncSession, location: Location) -> None:
        location.is_active = False
        await db.commit()


location_service = LocationService()
