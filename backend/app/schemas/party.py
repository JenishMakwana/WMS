import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SupplierBase(BaseModel):
    name: str
    contact_info: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class SupplierRead(SupplierBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class CustomerBase(BaseModel):
    name: str
    contact_info: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class CustomerRead(CustomerBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
