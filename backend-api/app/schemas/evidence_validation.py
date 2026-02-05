"""Pydantic schema for evidence validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.validator_result import ValidatorResult


class EvidenceValidationRead(BaseModel):
    """Schema for reading evidence validation records."""

    id: int
    user_id: int
    strategy_name: str
    source_filename: str | None
    text_hash: str | None
    # Note: extracted_text_encrypted intentionally omitted - sensitive data shouldn't be in API responses
    matches_json: ValidatorResult | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


