import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.party import Supplier, Customer
from app.schemas.party import SupplierCreate, SupplierUpdate, CustomerCreate, CustomerUpdate

class SupplierService:
    async def get_all(self, db: AsyncSession, user_id: uuid.UUID, active_only: bool = True) -> list[Supplier]:
        stmt = select(Supplier).where(Supplier.user_id == user_id)
        if active_only:
            stmt = stmt.where(Supplier.is_active == True)
        stmt = stmt.order_by(Supplier.name)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, supplier_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Supplier]:
        result = await db.execute(select(Supplier).where(Supplier.id == supplier_id, Supplier.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, data: SupplierCreate, user_id: uuid.UUID) -> Supplier:
        supplier = Supplier(**data.model_dump(), user_id=user_id)
        db.add(supplier)
        await db.commit()
        await db.refresh(supplier)
        return supplier

    async def update(self, db: AsyncSession, supplier: Supplier, data: SupplierUpdate) -> Supplier:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(supplier, field, value)
        await db.commit()
        await db.refresh(supplier)
        return supplier

    async def delete(self, db: AsyncSession, supplier: Supplier) -> None:
        supplier.is_active = False
        await db.commit()

class CustomerService:
    async def get_all(self, db: AsyncSession, user_id: uuid.UUID, active_only: bool = True) -> list[Customer]:
        stmt = select(Customer).where(Customer.user_id == user_id)
        if active_only:
            stmt = stmt.where(Customer.is_active == True)
        stmt = stmt.order_by(Customer.name)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, customer_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Customer]:
        result = await db.execute(select(Customer).where(Customer.id == customer_id, Customer.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, data: CustomerCreate, user_id: uuid.UUID) -> Customer:
        customer = Customer(**data.model_dump(), user_id=user_id)
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer

    async def update(self, db: AsyncSession, customer: Customer, data: CustomerUpdate) -> Customer:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        await db.commit()
        await db.refresh(customer)
        return customer

    async def delete(self, db: AsyncSession, customer: Customer) -> None:
        customer.is_active = False
        await db.commit()

supplier_service = SupplierService()
customer_service = CustomerService()
