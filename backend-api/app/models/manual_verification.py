"""manualVerification Model for user-submitted control verifications."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.compliance import Scan # prevent version conflict with circular import
    from app.models.user import User # prevent version conflict with circular import

class ManualVerification(Base):
    """Model for manual verification of controls by users."""

    __tablename__ = "manual_verification"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scan.id"), nullable=False)
    control_id: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    # Status: passed or failed
    status: Mapped[str] = mapped_column(String(20), nullable=False)  
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    scan: Mapped["Scan"] = relationship()
    user: Mapped["User"] = relationship()   