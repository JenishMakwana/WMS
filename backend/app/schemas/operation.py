import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.operation import OperationStatus, OperationType


# ── Stock Move (line item) ────────────────────────────────────────────────────

class StockMoveCreate(BaseModel):
    product_id: uuid.UUID
    demand_qty: Decimal = Field(..., gt=0)
    src_location_id: Optional[uuid.UUID] = None
    dest_location_id: Optional[uuid.UUID] = None


class StockMoveRead(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    product_sku: str
    product_uom: str
    demand_qty: Decimal
    done_qty: Optional[Decimal] = None
    src_location_id: Optional[uuid.UUID] = None
    src_location_name: Optional[str] = None
    dest_location_id: Optional[uuid.UUID] = None
    dest_location_name: Optional[str] = None

    class Config:
        from_attributes = True


# ── Operation ─────────────────────────────────────────────────────────────────

class OperationCreate(BaseModel):
    type: OperationType
    supplier: Optional[str] = None
    customer: Optional[str] = None
    supplier_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    src_location_id: Optional[uuid.UUID] = None
    dest_location_id: Optional[uuid.UUID] = None
    scheduled_date: Optional[datetime] = None
    moves: list[StockMoveCreate] = Field(default_factory=list)

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if isinstance(v, str):
            return v.upper()
        return v


class OperationUpdate(BaseModel):
    supplier: Optional[str] = None
    customer: Optional[str] = None
    supplier_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    src_location_id: Optional[uuid.UUID] = None
    dest_location_id: Optional[uuid.UUID] = None
    scheduled_date: Optional[datetime] = None


class OperationRead(BaseModel):
    id: uuid.UUID
    reference: str
    type: OperationType
    status: OperationStatus
    supplier: Optional[str] = None
    customer: Optional[str] = None
    supplier_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    supplier_name: Optional[str] = None
    customer_name: Optional[str] = None
    supplier_address: Optional[str] = None
    customer_address: Optional[str] = None
    notes: Optional[str] = None
    src_location_id: Optional[uuid.UUID] = None
    src_location_name: Optional[str] = None
    src_warehouse_name: Optional[str] = None
    src_warehouse_address: Optional[str] = None
    dest_location_id: Optional[uuid.UUID] = None
    dest_location_name: Optional[str] = None
    dest_warehouse_name: Optional[str] = None
    dest_warehouse_address: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    user_id: Optional[uuid.UUID] = None
    created_by_name: Optional[str] = None
    created_at: datetime
    moves: list[StockMoveRead] = []

    class Config:
        from_attributes = True


class OperationListRead(BaseModel):
    id: uuid.UUID
    reference: str
    type: OperationType
    status: OperationStatus
    supplier: Optional[str] = None
    customer: Optional[str] = None
    supplier_name: Optional[str] = None
    customer_name: Optional[str] = None
    supplier_address: Optional[str] = None
    customer_address: Optional[str] = None
    src_location_name: Optional[str] = None
    dest_location_name: Optional[str] = None
    src_warehouse_name: Optional[str] = None
    dest_warehouse_name: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    user_id: Optional[uuid.UUID] = None
    created_at: datetime
    move_count: int = 0

    class Config:
        from_attributes = True


# ── Ledger ────────────────────────────────────────────────────────────────────

class LedgerRead(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    product_sku: str
    location_id: uuid.UUID
    location_name: str
    warehouse_name: str
    operation_id: Optional[uuid.UUID] = None
    operation_reference: Optional[str] = None
    operation_type: Optional[OperationType] = None
    qty_change: Decimal
    balance_after: Decimal
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
