"""EvidenceValidation model for persisting validator outputs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class EvidenceValidation(Base):
    """Persisted validator output for an evidence scan."""

    __tablename__ = "evidence_validation"

    id: Mapped[int] = mapped_column(primary_key=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    strategy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_filename: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # sha256 of extracted text (hex)
    text_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Optional encrypted extracted text (or excerpt) for secure traceability
    extracted_text_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Validator output JSON (matched/missing/summary)
    matches_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # success | error
    status: Mapped[str] = mapped_column(String(25), nullable=False, default="success")

    # Relationships
    user: Mapped["User"] = relationship(back_populates="evidence_validations")
