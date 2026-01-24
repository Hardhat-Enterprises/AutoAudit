"""Compliance models for audit scans."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.m365_connection import M365Connection
    from app.models.scan_result import ScanResult
    from app.models.user import User


class Scan(Base):
    """Scan represents an individual compliance scan run against a cloud connection."""

    __tablename__ = "scan"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Direct user ownership
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Cloud connection FKs (only one should be non-null per scan)
    m365_connection_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("m365_connection.id"), nullable=True
    )
    azure_connection_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("azure_connection.id"), nullable=True
    )
    gcp_connection_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("gcp_connection.id"), nullable=True
    )
    aws_connection_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("aws_connection.id"), nullable=True
    )

    # Framework/benchmark targeting
    framework: Mapped[str] = mapped_column(String(50), nullable=False)
    benchmark: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    # Note: control_ids removed - ScanResult records track which controls were selected

    # Scan timing and status
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")

    # Results summary
    compliance_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    total_controls: Mapped[int] = mapped_column(default=0)
    passed_count: Mapped[int] = mapped_column(default=0)
    failed_count: Mapped[int] = mapped_column(default=0)
    skipped_count: Mapped[int] = mapped_column(default=0)
    error_count: Mapped[int] = mapped_column(default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="scans")
    m365_connection: Mapped[Optional["M365Connection"]] = relationship(
        back_populates="scans"
    )
    results: Mapped[list["ScanResult"]] = relationship(back_populates="scan")

    @property
    def connection_name(self) -> str | None:
        """Convenience field for API/UI display."""
        if self.m365_connection is not None:
            return self.m365_connection.name
        return None
