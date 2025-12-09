from enum import Enum
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Role(str, Enum):
    """User roles for role-based access control."""
    ADMIN = "admin"
    AUDITOR = "auditor"
    VIEWER = "viewer"


class User(SQLAlchemyBaseUserTable[int], Base):
    """User model for authentication and authorization."""
    __tablename__ = "user"

    # Override id to use integer primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Add custom role field
    role: Mapped[str] = mapped_column(
        String(20),
        default=Role.VIEWER.value,
        nullable=False
    )

    # Inherited from SQLAlchemyBaseUserTable:
    # - email: str
    # - hashed_password: str
    # - is_active: bool
    # - is_superuser: bool
    # - is_verified: bool
