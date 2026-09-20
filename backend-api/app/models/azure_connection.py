"""Azure Connection model for storing Microsoft Azure credentials."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AzureConnection(Base):
    """AzureConnection stores credentials for connecting to an Azure subscription.

    The client_secret is encrypted at rest using Fernet symmetric encryption.
    Users can have multiple Azure connections (e.g., for different subscriptions).
    """

    __tablename__ = "azure_connection"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Human-readable name for this connection (e.g., "Production Subscription")
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Azure AD tenant GUID
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Azure AD App Registration client ID
    client_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Encrypted client secret (Fernet encryption)
    encrypted_client_secret: Mapped[str] = mapped_column(Text, nullable=False)

    # Azure subscription ID
    subscription_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Soft active flag - allows deactivating without deleting
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="azure_connections")
