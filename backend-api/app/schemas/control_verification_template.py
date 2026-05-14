"""Pydantic schemas for ControlVerificationTemplate."""
 
from datetime import datetime
from typing import Literal, Optional
 
from pydantic import BaseModel, ConfigDict, Field, model_validator
 
 
# Allowed severity values. Enforced at the API layer; the DB still stores
# this as String(20) for forward compatibility.
Severity = Literal["high", "medium", "low"]
 
# Allowed evidence_type values for templates that require uploaded evidence.
EvidenceType = Literal["screenshot", "pdf_export", "comment_only"]
 
 
class ControlVerificationTemplateCreate(BaseModel):
    """Schema for creating a new verification template.
 
    The (framework, benchmark, version, control_id) tuple uniquely identifies
    the template. A duplicate tuple returns 409 Conflict at the endpoint.
    """
 
    framework: str = Field(..., max_length=50)
    benchmark: str = Field(..., max_length=100)
    version: str = Field(..., max_length=20)
    control_id: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    instructions: str
    keywords: list[str]
    severity: Severity
    evidence_type: Optional[EvidenceType] = None
 
 
class ControlVerificationTemplateUpdate(BaseModel):
    """Schema for partial update of a verification template.
 
    Only fields provided are applied. The (framework, benchmark, version,
    control_id) tuple is the resource key and is therefore not updatable —
    callers wanting to relocate a template should DELETE and POST.
 
    Non-nullable columns (title, instructions, keywords, severity) must not
    be set to None explicitly; doing so returns 422 rather than letting the
    DB raise a 500 on the integrity error.
    """
 
    title: Optional[str] = Field(None, max_length=200)
    instructions: Optional[str] = None
    keywords: Optional[list[str]] = None
    severity: Optional[Severity] = None
    evidence_type: Optional[EvidenceType] = None
 
    @model_validator(mode="after")
    def reject_explicit_nulls_on_required_fields(self) -> "ControlVerificationTemplateUpdate":
        """Reject explicit null values for fields that are non-nullable in the DB.
 
        Pydantic's exclude_unset behaviour treats `{"title": null}` and
        `{}` differently — the former is "set to None", the latter is "not
        set". The endpoint's update loop uses exclude_unset=True, so an
        explicit null would attempt to write NULL to a NOT NULL column and
        surface as a 500. Rejecting at validation time gives the client a
        clean 422 instead.
        """
        explicit_nulls = [
            name
            for name in ("title", "instructions", "keywords", "severity")
            if name in self.model_fields_set and getattr(self, name) is None
        ]
        if explicit_nulls:
            raise ValueError(
                "Fields cannot be set to null: " + ", ".join(explicit_nulls)
            )
        return self
 
 
class ControlVerificationTemplateRead(BaseModel):
    """Schema for reading a verification template."""
 
    model_config = ConfigDict(from_attributes=True)
 
    id: int
    framework: str
    benchmark: str
    version: str
    control_id: str
    title: str
    instructions: str
    keywords: list[str]
    severity: str
    evidence_type: Optional[str]
    created_at: datetime
    updated_at: datetime