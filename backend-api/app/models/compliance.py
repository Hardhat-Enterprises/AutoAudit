"""Compliance models for audit scans and findings."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Tenant(Base):
    """Tenant represents a company or organization being audited."""
    __tablename__ = "tenant"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_tenant_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    scans: Mapped[list["Scan"]] = relationship(back_populates="tenant")


class Rule(Base):
    """Rule represents a compliance control from a framework (e.g., CIS, Essential 8)."""
    __tablename__ = "rule"

    id: Mapped[int] = mapped_column(primary_key=True)
    framework: Mapped[str] = mapped_column(String(100), nullable=False)
    control_key: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    issues: Mapped[list["Issue"]] = relationship(back_populates="rule")


class Scan(Base):
    """Scan represents an individual compliance scan run against a tenant."""
    __tablename__ = "scan"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenant.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="running")
    compliance_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    total_controls: Mapped[int] = mapped_column(default=0)
    passed_count: Mapped[int] = mapped_column(default=0)
    failed_count: Mapped[int] = mapped_column(default=0)
    not_tested_count: Mapped[int] = mapped_column(default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="scans")
    issues: Mapped[list["Issue"]] = relationship(back_populates="scan")


class Issue(Base):
    """Issue represents a finding from a compliance scan."""
    __tablename__ = "issue"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scan.id"), nullable=False)
    rule_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rule.id"), nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    evidence: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    scan: Mapped["Scan"] = relationship(back_populates="issues")
    rule: Mapped[Optional["Rule"]] = relationship(back_populates="issues")
