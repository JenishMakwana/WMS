import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase

from app.core.config import settings
from app.db.user_db import get_user_db
from app.models.user import User
from app.utils.email import send_reset_password_email


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"\n[CoreInventory] NEW USER REGISTERED: {user.email}")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print("\n" + "*"*60)
        print(f"[CoreInventory SUCCESS] on_after_forgot_password TRIGGERED!")
        print(f"[CoreInventory SUCCESS] User found: {user.email}")
        print(f"[CoreInventory SUCCESS] Token: {token[:10]}...")
        print("*"*60 + "\n")
        await send_reset_password_email(email=user.email, token=token)

    async def get_by_email(self, email: str) -> User:
        """Log whenever a user is looked up by email."""
        print(f"[CoreInventory] Looking up user by email: {email}")
        try:
            user = await super().get_by_email(email)
            print(f"[CoreInventory] Found user in DB: {user.email}")
            return user
        except Exception:
            print(f"[CoreInventory] User '{email}' NOT FOUND in DB.")
            raise

    async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
        print(f"[CoreInventory] Password successfully reset for: {user.email}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"[CoreInventory] Verification requested for: {user.email}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
