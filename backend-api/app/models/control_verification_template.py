"""ControlVerificationTemplate model.
 
Stores per-control auditor instructions, keywords, and severity for the manual
controls that AutoAudit cannot automate via the M365 collectors. Each row is
uniquely identified by the (framework, benchmark, version, control_id) tuple
so that the same control_id can carry different instructions across CIS
benchmark versions (e.g. "1.1.2" in v3.1.0 vs v6.0.0) and across frameworks
(e.g. CIS M365 vs future Azure benchmarks).
 
Powers the semi-automated manual verification workflow: the auditor opens a
pending manual control, sees the instructions, uploads evidence, and the
validator matches the keywords to suggest a verdict.
 
Keywords are stored as JSONB to match the patterns already used by
EvidenceValidation.matches_json and ScanResult.evidence.
"""
 
from datetime import datetime
from typing import Optional
 
from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
 
from app.db.base import Base
 
 
class ControlVerificationTemplate(Base):
    """Verification template for a single manual control within a framework/benchmark/version."""
 
    __tablename__ = "control_verification_template"
 
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
 
    # Framework/benchmark/version tuple — mirrors Scan.framework/benchmark/version
    # so the lookup pattern (and column types) are consistent across the schema.
    framework: Mapped[str] = mapped_column(String(50), nullable=False)
    benchmark: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
 
    # CIS control identifier within the (framework, benchmark, version) above,
    # e.g. "1.1.2". Must match scan_result.control_id for the same tuple.
    control_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
 
    # Human-readable control title from the benchmark.
    title: Mapped[str] = mapped_column(String(200), nullable=False)
 
    # Numbered, portal-specific auditor instructions.
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
 
    # List of keywords expected to appear in compliant evidence.
    # JSONB so we can index/query individual keywords later if needed.
    keywords: Mapped[list] = mapped_column(JSONB, nullable=False)
 
    # Risk severity: "high" | "medium" | "low". Enforced at the API layer via
    # the Pydantic Literal type on the Create/Update schemas.
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
 
    # Expected evidence format: "screenshot" | "pdf_export" | "comment_only".
    evidence_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
 
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
 
    __table_args__ = (
        UniqueConstraint(
            "framework",
            "benchmark",
            "version",
            "control_id",
            name="uq_template_framework_benchmark_version_control",
        ),
    )