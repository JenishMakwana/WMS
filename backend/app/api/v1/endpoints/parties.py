import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import current_active_user
from app.db.session import get_async_session
from app.models.user import User
from app.schemas.party import SupplierCreate, SupplierRead, SupplierUpdate, CustomerCreate, CustomerRead, CustomerUpdate
from app.services.party_service import supplier_service, customer_service

router = APIRouter(tags=["parties"])

# ── Suppliers ────────────────────────────────────────────────────────────────

@router.get("/suppliers/", response_model=list[SupplierRead])
async def list_suppliers(
    active_only: bool = True,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    return await supplier_service.get_all(db, user_id=user.id, active_only=active_only)

@router.post("/suppliers/", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    return await supplier_service.create(db, data, user_id=user.id)

@router.get("/suppliers/{supplier_id}", response_model=SupplierRead)
async def get_supplier(
    supplier_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    supplier = await supplier_service.get_by_id(db, supplier_id, user_id=user.id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.patch("/suppliers/{supplier_id}", response_model=SupplierRead)
async def update_supplier(
    supplier_id: uuid.UUID,
    data: SupplierUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    supplier = await supplier_service.get_by_id(db, supplier_id, user_id=user.id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return await supplier_service.update(db, supplier, data)

@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_supplier(
    supplier_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    supplier = await supplier_service.get_by_id(db, supplier_id, user_id=user.id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    await supplier_service.delete(db, supplier)

# ── Customers ────────────────────────────────────────────────────────────────

@router.get("/customers/", response_model=list[CustomerRead])
async def list_customers(
    active_only: bool = True,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    return await customer_service.get_all(db, user_id=user.id, active_only=active_only)

@router.post("/customers/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    return await customer_service.create(db, data, user_id=user.id)

@router.get("/customers/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    customer = await customer_service.get_by_id(db, customer_id, user_id=user.id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.patch("/customers/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: uuid.UUID,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    customer = await customer_service.get_by_id(db, customer_id, user_id=user.id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return await customer_service.update(db, customer, data)

@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_customer(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    customer = await customer_service.get_by_id(db, customer_id, user_id=user.id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    await customer_service.delete(db, customer)
