import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.users import current_active_user
from app.db.session import get_async_session
from app.models.product import Product
from app.models.product_category import ProductCategory
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.product import ProductCreate, ProductListRead, ProductRead, ProductUpdate
from app.services.product_service import product_service

router = APIRouter(tags=["products"])

# ── Categories ────────────────────────────────────────────────────────────────

cat_router = APIRouter(prefix="/categories")


@cat_router.get("/", response_model=list[CategoryRead])
async def list_categories(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(select(ProductCategory).where(ProductCategory.user_id == user.id).order_by(ProductCategory.name))
    return result.scalars().all()


@cat_router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    cat = ProductCategory(**data.model_dump(), user_id=user.id)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


@cat_router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(select(ProductCategory).where(ProductCategory.id == category_id, ProductCategory.user_id == user.id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    await db.commit()
    await db.refresh(cat)
    return cat


@cat_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(select(ProductCategory).where(ProductCategory.id == category_id, ProductCategory.user_id == user.id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(cat)
    await db.commit()


# ── Products ──────────────────────────────────────────────────────────────────

prod_router = APIRouter(prefix="/products")


@prod_router.get("/", response_model=list[ProductListRead])
async def list_products(
    search: Optional[str] = Query(None, description="Search by name or SKU"),
    category_id: Optional[uuid.UUID] = Query(None),
    low_stock_only: bool = Query(False),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    return await product_service.get_all(
        db,
        user_id=user.id,
        search=search,
        category_id=category_id,
        active_only=active_only,
        low_stock_only=low_stock_only,
    )


@prod_router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    existing = await product_service.get_by_sku(db, data.sku, user_id=user.id)
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    product = await product_service.create(db, data, user_id=user.id)
    return await product_service.get_by_id(db, product.id, user_id=user.id)


@prod_router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    product = await product_service.get_by_id(db, product_id, user_id=user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@prod_router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(select(Product).where(Product.id == product_id, Product.user_id == user.id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if data.sku and data.sku != product.sku:
        existing = await product_service.get_by_sku(db, data.sku, user_id=user.id)
        if existing and existing.id != product.id:
            raise HTTPException(status_code=400, detail="SKU already exists")

    await product_service.update(db, product, data)
    return await product_service.get_by_id(db, product_id, user_id=user.id)


@prod_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await db.execute(select(Product).where(Product.id == product_id, Product.user_id == user.id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await product_service.delete(db, product)
