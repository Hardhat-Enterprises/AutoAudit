"""ScanResult model for individual control results within a scan."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.compliance import Scan


class ScanResult(Base):
    """Individual control result within a scan."""

    __tablename__ = "scan_result"
    __table_args__ = (
        UniqueConstraint("scan_id", "control_id", name="uq_scan_result_scan_control"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scan.id"), nullable=False)
    control_id: Mapped[str] = mapped_column(String(50), nullable=False)

    # Status: pending, passed, failed, error, skipped
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    scan: Mapped["Scan"] = relationship(back_populates="results")
