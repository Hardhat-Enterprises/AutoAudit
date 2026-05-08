"""Pydantic schemas for ControlVerificationTemplate."""

from datetime import datetime

from pydantic import BaseModel, Field


class ControlVerificationTemplateCreate(BaseModel):
    """Schema for creating a new verification template."""

    control_id: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    instructions: str
    keywords: list[str]
    severity: str = Field(..., max_length=20)
    evidence_type: str | None = Field(None, max_length=50)


class ControlVerificationTemplateUpdate(BaseModel):
    """Schema for partial update of a verification template.

    All fields optional — only provided fields are applied.
    control_id is intentionally not updatable (it's the resource key).
    """

    title: str | None = Field(None, max_length=200)
    instructions: str | None = None
    keywords: list[str] | None = None
    severity: str | None = Field(None, max_length=20)
    evidence_type: str | None = Field(None, max_length=50)


class ControlVerificationTemplateRead(BaseModel):
    """Schema for reading a verification template."""

    id: int
    control_id: str
    title: str
    instructions: str
    keywords: list[str]
    severity: str
    evidence_type: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True