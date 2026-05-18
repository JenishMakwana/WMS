from fastapi import APIRouter, Depends, Request

from app.core.users import current_active_user, fastapi_users
from app.core.auth_backend import auth_backend
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

# Add a simple debug route to test connectivity
@router.get("/test-auth-router")
async def test_auth_router():
    return {"message": "Auth router is reachable"}


# Register fastapi-users routes:
# POST /register
# POST /jwt/login
# POST /jwt/logout
# POST /forgot-password
# POST /reset-password
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@router.get("/me", response_model=UserRead, tags=["auth"])
async def get_me(user: User = Depends(current_active_user)):
    """Return the currently authenticated user with role information."""
    return user
