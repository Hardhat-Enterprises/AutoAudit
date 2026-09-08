from fastapi_users import schemas
from app.models.user import Role


class UserRead(schemas.BaseUser[int]):
    role: Role
    first_name: str | None = None
    last_name: str | None = None
    organization_name: str | None = None


class UserCreate(schemas.BaseUserCreate):
    role: Role = Role.VIEWER

    first_name: str | None = None
    last_name: str | None = None
    organization_name: str | None = None


class UserRegister(schemas.BaseUserCreate):
    first_name: str | None = None
    last_name: str | None = None
    organization_name: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    role: Role | None = None

    first_name: str | None = None
    last_name: str | None = None
    organization_name: str | None = None