# backend/app/schemas/compliance.py
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class IssueIn(BaseModel):
    rule_id: Optional[int] = None
    priority: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    result: Optional[str] = None
    evidence: Optional[Any] = None

class ScanIn(BaseModel):
    tenant_id: int = 1
    status: Optional[str] = "completed"
    compliance_score: Optional[float] = None
    total_controls: Optional[int] = 0
    passed_count: Optional[int] = 0
    failed_count: Optional[int] = 0
    not_tested_count: Optional[int] = 0
    notes: Optional[str] = None
    issues: Optional[List[IssueIn]] = []

# Response models
class IssueOut(BaseModel):
    id: int
    scan_id: int
    rule_id: Optional[int]
    priority: Optional[str]
    title: Optional[str]
    description: Optional[str]
    result: Optional[str]
    evidence: Optional[Any]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class ScanOut(BaseModel):
    id: int
    tenant_id: int
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    status: Optional[str]
    compliance_score: Optional[float]
    total_controls: Optional[int]
    passed_count: Optional[int]
    failed_count: Optional[int]
    not_tested_count: Optional[int]
    notes: Optional[str]

    class Config:
        from_attributes = True

class ScanReportOut(BaseModel):
    scan: ScanOut
    issues: List[IssueOut]
