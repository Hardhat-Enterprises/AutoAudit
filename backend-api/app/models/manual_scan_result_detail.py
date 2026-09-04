"""ManualScanResultDetail model for extra data on manually verified controls."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.scan_result import ScanResult
    from app.models.user import User


class ManualScanResultDetail(Base):
    """Extra detail for scan results that were manually verified."""

    __tablename__ = "manual_scan_result_detail"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_result_id: Mapped[int] = mapped_column(
        ForeignKey("scan_result.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    scan_result: Mapped["ScanResult"] = relationship()
    user: Mapped["User"] = relationship()