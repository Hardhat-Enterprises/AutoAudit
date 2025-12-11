"""M365 Connection model for storing Microsoft 365 tenant credentials."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.compliance import Scan


class M365Connection(Base):
    """M365Connection stores credentials for connecting to a Microsoft 365 tenant.

    The client_secret is encrypted at rest using Fernet symmetric encryption.
    Users can have multiple M365 connections (e.g., for different clients/tenants).
    """

    __tablename__ = "m365_connection"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Human-readable name for this connection (e.g., "Contoso Production")
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Azure AD / Entra ID tenant GUID
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Azure AD App Registration client ID
    client_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Encrypted client secret (Fernet encryption)
    encrypted_client_secret: Mapped[str] = mapped_column(Text, nullable=False)

    # Soft active flag - allows deactivating without deleting
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="m365_connections")
    scans: Mapped[list["Scan"]] = relationship(back_populates="m365_connection")
