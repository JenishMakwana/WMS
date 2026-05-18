import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import current_active_user
from app.db.session import get_async_session
from app.models.user import User
from app.schemas.location import LocationCreate, LocationRead, LocationUpdate
from app.services.location_service import location_service
from app.services.warehouse_service import warehouse_service

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/", response_model=list[LocationRead])
async def list_locations(
    warehouse_id: Optional[uuid.UUID] = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    locations = await location_service.get_all(db, user_id=user.id, warehouse_id=warehouse_id, active_only=active_only)
    return [
        LocationRead(
            **{c.name: getattr(loc, c.name) for c in loc.__table__.columns},
            warehouse_name=loc.warehouse.name if loc.warehouse else None,
        )
        for loc in locations
    ]


@router.post("/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(
    data: LocationCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    wh = await warehouse_service.get_by_id(db, data.warehouse_id, user_id=user.id)
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    loc = await location_service.create(db, data, user_id=user.id)
    return LocationRead(
        **{c.name: getattr(loc, c.name) for c in loc.__table__.columns},
        warehouse_name=wh.name,
    )


@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    loc = await location_service.get_by_id(db, location_id, user_id=user.id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return LocationRead(
        **{c.name: getattr(loc, c.name) for c in loc.__table__.columns},
        warehouse_name=loc.warehouse.name if loc.warehouse else None,
    )


@router.patch("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: uuid.UUID,
    data: LocationUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    loc = await location_service.get_by_id(db, location_id, user_id=user.id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    updated = await location_service.update(db, loc, data)
    return LocationRead(
        **{c.name: getattr(updated, c.name) for c in updated.__table__.columns},
        warehouse_name=updated.warehouse.name if updated.warehouse else None,
    )


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_location(
    location_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    loc = await location_service.get_by_id(db, location_id, user_id=user.id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    await location_service.delete(db, loc)
