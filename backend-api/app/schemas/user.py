from fastapi_users import schemas
from pydantic import EmailStr
from app.models.user import Role


class UserRead(schemas.BaseUser[int]):
    """Schema for reading user data."""
    role: Role


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user."""
    role: Role = Role.VIEWER


class UserRegister(schemas.BaseUserCreate):
    """
    Public registration schema.

    Intentionally does NOT expose role/is_superuser/etc so a self-registering
    user cannot elevate privileges.
    """


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data."""
    role: Role | None = None
