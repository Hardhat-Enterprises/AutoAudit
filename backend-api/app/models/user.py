from enum import Enum
from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.compliance import Scan
    from app.models.evidence_validation import EvidenceValidation
    from app.models.m365_connection import M365Connection
    from app.models.contact import ContactSubmission, SubmissionHistory, SubmissionNote
    from app.models.oauth_account import OAuthAccount


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

    # Relationships
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    m365_connections: Mapped[list["M365Connection"]] = relationship(
        back_populates="user"
    )
    scans: Mapped[list["Scan"]] = relationship(back_populates="user")
    evidence_validations: Mapped[list["EvidenceValidation"]] = relationship(
        back_populates="user"
    )
    assigned_submissions: Mapped[list["ContactSubmission"]] = relationship(
        back_populates="assigned_user"
    )
    submission_notes: Mapped[list["SubmissionNote"]] = relationship(
        back_populates="admin_user"
    )
    submission_history: Mapped[list["SubmissionHistory"]] = relationship(
        back_populates="admin_user"
    )
