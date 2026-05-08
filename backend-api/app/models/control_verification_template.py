"""ControlVerificationTemplate model.

Stores per-control auditor instructions, keywords, and severity for the 14
manual controls that AutoAudit cannot automate via the M365 collectors.
Each row corresponds to one CIS control_id (e.g. "1.1.2") and powers the
semi-automated manual verification workflow: the auditor opens a pending
manual control, sees the instructions, uploads evidence, and the validator
matches the keywords to suggest a verdict.

Keywords are stored as JSONB to match the patterns already used by
EvidenceValidation.matches_json and ScanResult.evidence.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ControlVerificationTemplate(Base):
    """Verification template for a single manual CIS control.

    One row per control_id (enforced via unique constraint).
    """

    __tablename__ = "control_verification_template"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # CIS control identifier, e.g. "1.1.2". Must match scan_result.control_id.
    control_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    # Human-readable control title from the CIS benchmark.
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # Numbered, portal-specific auditor instructions.
    instructions: Mapped[str] = mapped_column(Text, nullable=False)

    # List of keywords expected to appear in compliant evidence.
    # JSONB so we can index/query individual keywords later if needed.
    keywords: Mapped[list] = mapped_column(JSONB, nullable=False)

    # Risk severity: "high" | "medium" | "low".
    severity: Mapped[str] = mapped_column(String(20), nullable=False)

    # Expected evidence format: "screenshot" | "pdf_export" | "comment_only".
    evidence_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )