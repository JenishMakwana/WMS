import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WarehouseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    short_code: str = Field(..., min_length=1, max_length=20)
    address: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    short_code: Optional[str] = Field(None, min_length=1, max_length=20)
    address: Optional[str] = None
    is_active: Optional[bool] = None


class WarehouseRead(WarehouseBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
