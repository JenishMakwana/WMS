import uuid
from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr

from app.models.user import UserRole


class UserRead(schemas.BaseUser[uuid.UUID]):
    full_name: str
    role: UserRole

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    full_name: str
    role: UserRole = UserRole.WAREHOUSE_STAFF


class UserUpdate(schemas.BaseUserUpdate):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
