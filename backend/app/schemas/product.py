import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    unit_of_measure: str = Field(default="pcs", max_length=50)
    category_id: Optional[uuid.UUID] = None


class ProductCreate(ProductBase):
    quantity: Optional[Decimal] = Field(default=None, ge=0)
    initial_location_id: Optional[uuid.UUID] = None  # where to put initial stock


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    category_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None


class StockByLocation(BaseModel):
    location_id: uuid.UUID
    location_name: str
    warehouse_name: str
    quantity: Decimal

    class Config:
        from_attributes = True


class ProductRead(ProductBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    category_name: Optional[str] = None
    total_stock: Decimal = Decimal("0")
    stock_by_location: list[StockByLocation] = []

    class Config:
        from_attributes = True


class ProductListRead(BaseModel):
    """Lightweight version for list views — no per-location breakdown."""
    id: uuid.UUID
    name: str
    sku: str
    unit_of_measure: str
    category_name: Optional[str] = None
    total_stock: Decimal = Decimal("0")
    is_active: bool

    class Config:
        from_attributes = True
