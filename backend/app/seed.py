"""
Seed script — populates the database with demo data for development.

Usage:
    cd backend
    python -m app.seed
"""
import asyncio
import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker, engine, Base
from app.models.user import User, UserRole
from app.models.warehouse import Warehouse
from app.models.location import Location
from app.models.product_category import ProductCategory
from app.models.product import Product
from app.models.stock_entry import StockEntry
import app.models  # noqa — register all models


async def seed():
    print("⬆  Running migrations...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        print("🌱 Seeding demo data...")

        # ── Users ──────────────────────────────────────────────────────────────
        from fastapi_users.password import PasswordHelper
        ph = PasswordHelper()

        manager = User(
            id=uuid.uuid4(),
            email="manager@coreinventory.com",
            hashed_password=ph.hash("Manager123!"),
            full_name="Raj Patel",
            role=UserRole.INVENTORY_MANAGER,
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )
        staff = User(
            id=uuid.uuid4(),
            email="staff@coreinventory.com",
            hashed_password=ph.hash("Staff123!"),
            full_name="Priya Shah",
            role=UserRole.WAREHOUSE_STAFF,
            is_active=True,
            is_superuser=False,
            is_verified=True,
        )
        db.add_all([manager, staff])
        await db.flush()

        # ── Warehouses ─────────────────────────────────────────────────────────
        wh_main = Warehouse(name="Main Warehouse", short_code="WH01", address="Plot 12, Industrial Area, Surat", user_id=manager.id)
        wh_prod = Warehouse(name="Production Floor", short_code="WH02", address="Plot 12, Industrial Area, Surat", user_id=manager.id)
        db.add_all([wh_main, wh_prod])
        await db.flush()

        # ── Locations ──────────────────────────────────────────────────────────
        # Note: Location model might not have user_id, let's check
        rack_a = Location(name="Rack A", short_code="RA", warehouse_id=wh_main.id)
        rack_b = Location(name="Rack B", short_code="RB", warehouse_id=wh_main.id)
        rack_c = Location(name="Rack C", short_code="RC", warehouse_id=wh_main.id)
        prod_floor = Location(name="Production Floor", short_code="PF", warehouse_id=wh_prod.id)
        db.add_all([rack_a, rack_b, rack_c, prod_floor])
        await db.flush()

        # ── Categories ─────────────────────────────────────────────────────────
        cat_raw = ProductCategory(name="Raw Materials", user_id=manager.id)
        cat_fin = ProductCategory(name="Finished Goods", user_id=manager.id)
        cat_pack = ProductCategory(name="Packaging", user_id=manager.id)
        db.add_all([cat_raw, cat_fin, cat_pack])
        await db.flush()

        # ── Products + initial stock ───────────────────────────────────────────
        products_data = [
            ("Steel Rods",    "SR-001", "kg",  cat_raw.id,  Decimal("500"), rack_a.id),
            ("Copper Wire",   "CW-001", "m",   cat_raw.id,  Decimal("200"), rack_a.id),
            ("Aluminium Sheet","AS-001","kg",  cat_raw.id,  Decimal("100"), rack_b.id),
            ("Steel Frame",   "SF-001", "pcs", cat_fin.id,  Decimal("30"),  rack_c.id),
            ("Copper Coil",   "CC-001", "pcs", cat_fin.id,  Decimal("50"),  rack_c.id),
            ("Bubble Wrap",   "BW-001", "m",   cat_pack.id, Decimal("0"),   rack_b.id),
        ]

        for name, sku, uom, cat_id, stock, loc_id in products_data:
            p = Product(
                name=name, sku=sku, unit_of_measure=uom,
                category_id=cat_id, user_id=manager.id
            )
            db.add(p)
            await db.flush()
            if stock > 0:
                db.add(StockEntry(product_id=p.id, location_id=loc_id, quantity=stock))

        await db.commit()
        print("✅ Seed complete!")
        print()
        print("  Login credentials:")
        print("  Manager  →  manager@coreinventory.com  /  Manager123!")
        print("  Staff    →  staff@coreinventory.com    /  Staff123!")


if __name__ == "__main__":
    asyncio.run(seed())
