"""Pydantic schema for validator summary counts."""

from pydantic import BaseModel, Field


class ValidatorSummary(BaseModel):
    """Summary counts for validator results."""

    matchedCount: int = Field(..., description="Number of terms found")
    totalTerms: int = Field(..., description="Total terms checked")


