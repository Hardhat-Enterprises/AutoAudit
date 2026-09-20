"""AWS Connection model for storing Amazon Web Services credentials."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AWSConnection(Base):
    """AWSConnection stores credentials for connecting to an AWS account.

    The secret_access_key is encrypted at rest using Fernet symmetric encryption.
    Users can have multiple AWS connections (e.g., for different accounts/regions).
    """

    __tablename__ = "aws_connection"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Human-readable name for this connection (e.g., "Production Account")
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # AWS account ID (12-digit number)
    account_id: Mapped[str] = mapped_column(String(20), nullable=False)

    # IAM access key ID
    access_key_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Encrypted IAM secret access key (Fernet encryption)
    encrypted_secret_access_key: Mapped[str] = mapped_column(Text, nullable=False)

    # AWS region (e.g., "us-east-1")
    region: Mapped[str] = mapped_column(String(50), nullable=False, default="us-east-1")

    # Soft active flag - allows deactivating without deleting
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="aws_connections")
