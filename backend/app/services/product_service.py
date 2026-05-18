import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.product_category import ProductCategory
from app.models.stock_entry import StockEntry
from app.models.location import Location
from app.models.warehouse import Warehouse
from app.schemas.product import ProductCreate, ProductListRead, ProductRead, ProductUpdate, StockByLocation


class ProductService:

    async def get_all(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        search: Optional[str] = None,
        category_id: Optional[uuid.UUID] = None,
        active_only: bool = True,
        low_stock_only: bool = False,
    ) -> list[ProductListRead]:
        stmt = (
            select(Product)
            .options(selectinload(Product.category), selectinload(Product.stock_entries))
            .where(Product.user_id == user_id)
            .order_by(Product.name)
        )
        if active_only:
            stmt = stmt.where(Product.is_active == True)
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if search:
            stmt = stmt.where(
                Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%")
            )

        result = await db.execute(stmt)
        products = result.scalars().all()

        out = []
        for p in products:
            total = sum((e.quantity for e in p.stock_entries), Decimal("0"))
            out.append(
                ProductListRead(
                    id=p.id,
                    name=p.name,
                    sku=p.sku,
                    unit_of_measure=p.unit_of_measure,
                    category_name=p.category.name if p.category else None,
                    total_stock=total,
                    is_active=p.is_active,
                )
            )
        return out

    async def get_by_id(self, db: AsyncSession, product_id: uuid.UUID, user_id: uuid.UUID) -> Optional[ProductRead]:
        result = await db.execute(
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.stock_entries).selectinload(StockEntry.location).selectinload(Location.warehouse),
            )
            .where(Product.id == product_id, Product.user_id == user_id)
        )
        p = result.scalar_one_or_none()
        if not p:
            return None

        stock_by_loc = [
            StockByLocation(
                location_id=e.location_id,
                location_name=e.location.name,
                warehouse_name=e.location.warehouse.name,
                quantity=e.quantity,
            )
            for e in p.stock_entries
            if e.quantity > 0
        ]
        total = sum((s.quantity for s in stock_by_loc), Decimal("0"))

        return ProductRead(
            **{c.name: getattr(p, c.name) for c in p.__table__.columns},
            category_name=p.category.name if p.category else None,
            total_stock=total,
            stock_by_location=stock_by_loc,
        )

    async def get_by_sku(self, db: AsyncSession, sku: str, user_id: uuid.UUID) -> Optional[Product]:
        result = await db.execute(select(Product).where(Product.sku == sku, Product.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, data: ProductCreate, user_id: uuid.UUID) -> Product:
        product_data = data.model_dump(exclude={"quantity", "initial_location_id"})
        product = Product(**product_data, user_id=user_id)
        db.add(product)
        await db.flush()  # get ID before creating stock entry

        # Seed initial stock if provided
        if data.quantity and data.quantity > 0 and data.initial_location_id:
            entry = StockEntry(
                product_id=product.id,
                location_id=data.initial_location_id,
                quantity=data.quantity,
            )
            db.add(entry)

        await db.commit()
        await db.refresh(product)
        return product

    async def update(self, db: AsyncSession, product: Product, data: ProductUpdate) -> Product:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        await db.commit()
        await db.refresh(product)
        return product

    async def delete(self, db: AsyncSession, product: Product) -> None:
        product.is_active = False
        await db.commit()


product_service = ProductService()
