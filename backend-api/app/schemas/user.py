from fastapi_users import schemas
from pydantic import EmailStr
from app.models.user import Role


class UserRead(schemas.BaseUser[int]):
    """Schema for reading user data."""
    role: Role


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user."""
    role: Role = Role.VIEWER


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data."""
    role: Role | None = None
