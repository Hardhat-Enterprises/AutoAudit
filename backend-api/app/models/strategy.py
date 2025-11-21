from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, Field


class Strategy(BaseModel):
    """
    Metadata describing a mitigation / compliance strategy that the UI can present.
    """

    name: str = Field(..., example="CIS Microsoft 365 Audit")
    description: str = Field(..., example="Comprehensive Microsoft 365 security assessment based on CIS benchmarks")
    category: str = Field(..., example="Cloud Security")
    severity: str = Field(..., example="High")
    checker: str = Field(..., description="Fully-qualified checker class name or registry key")
    evidence_types: List[str] = Field(
        default_factory=list,
        example=["pdf", "png", "jpg", "txt", "docx", "log"],
        description="Extensions (lowercase, no dot) supported for this strategy",
    )


class ScanFinding(BaseModel):
    """
    Single finding emitted by a checker.
    """

    test_id: str
    sub_strategy: str
    detected_level: Union[str, int]
    pass_fail: str
    priority: str
    recommendation: str
    evidence: List[str]
    description: Optional[str] = None
    confidence: Optional[Union[str, int, float]] = None


class ScanResponse(BaseModel):
    """
    Standard scan response returned to the UI.
    """

    ok: bool = True
    findings: List[ScanFinding]
    reports: List[str]
    note: Optional[str] = None
