import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    short_code: str = Field(..., min_length=1, max_length=20)
    warehouse_id: uuid.UUID


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    short_code: Optional[str] = Field(None, min_length=1, max_length=20)
    is_active: Optional[bool] = None


class LocationRead(LocationBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    warehouse_name: Optional[str] = None  # populated via join

    class Config:
        from_attributes = True
