import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class AdjustmentLine(BaseModel):
    product_id: uuid.UUID
    location_id: uuid.UUID
    counted_qty: Decimal = Field(..., ge=0, description="Physical count — system calculates the delta")
    note: Optional[str] = None


class AdjustmentCreate(BaseModel):
    lines: list[AdjustmentLine] = Field(..., min_length=1)
    notes: Optional[str] = None
