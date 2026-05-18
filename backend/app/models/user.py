import uuid
from enum import Enum as PyEnum

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Boolean, Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class UserRole(str, PyEnum):
    ADMIN = "admin"
    INVENTORY_MANAGER = "inventory_manager"
    WAREHOUSE_STAFF = "warehouse_staff"


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    full_name = Column(String(100), nullable=False, default="")
    role = Column(
        Enum(UserRole, name="userrole"),
        nullable=False,
        default=UserRole.WAREHOUSE_STAFF,
    )
    is_active = Column(Boolean, default=True, nullable=False)
