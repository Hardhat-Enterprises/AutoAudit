"""Pydantic schema for validator output."""

from pydantic import BaseModel

from app.schemas.validator_match import ValidatorMatch
from app.schemas.validator_summary import ValidatorSummary


class ValidatorResult(BaseModel):
    """Validator output structure."""

    matched: list[ValidatorMatch]
    missing: list[str]
    summary: ValidatorSummary


