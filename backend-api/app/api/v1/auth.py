from fastapi import APIRouter, Depends
from fastapi_users import exceptions
from app.core.users import fastapi_users, auth_backend
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Login endpoint
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="",
)

# User management endpoints
users_router = APIRouter(prefix="/users", tags=["Users"])

# Get current user info
@users_router.get("/me", summary="Get my user information", response_model=UserRead)
async def read_users_me(user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return user


# Change password endpoint
from pydantic import BaseModel

class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@users_router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    user: User = Depends(get_current_user),
):
    """Change current user's password."""
    from app.core.users import get_user_manager
    from app.db.session import get_async_session
    from fastapi import Request

    # Create a mock request object for fastapi-users
    request = Request(scope={"type": "http"})

    async for session in get_async_session():
        async for user_manager in get_user_manager(session):
            try:
                # Verify current password
                verified, updated_password_hash = user_manager.password_helper.verify_and_update(
                    password_data.current_password, user.hashed_password
                )
                if not verified:
                    raise exceptions.InvalidPasswordException()

                # Hash new password
                new_hashed_password = user_manager.password_helper.hash(password_data.new_password)

                # Update user password
                user.hashed_password = new_hashed_password
                await session.commit()

                return {"message": "Password changed successfully"}

            except exceptions.InvalidPasswordException:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Invalid current password")


# Include users router
router.include_router(users_router)
