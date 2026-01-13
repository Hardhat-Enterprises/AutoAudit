"""Pydantic schemas for compliance scans."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ScanCreate(BaseModel):
    """Schema for creating a new scan."""

    m365_connection_id: int = Field(
        ..., description="ID of the M365 connection to scan"
    )
    framework: str = Field(
        ..., min_length=1, max_length=50, description="Framework (e.g., 'cis')"
    )
    benchmark: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Benchmark slug (e.g., 'microsoft-365-foundations')",
    )
    version: str = Field(
        ..., min_length=1, max_length=20, description="Version (e.g., 'v3.1.0')"
    )
    control_ids: list[str] | None = Field(
        None, description="Specific control IDs to scan (null = all)"
    )


class ScanResultRead(BaseModel):
    """Schema for reading scan result details."""

    id: int
    scan_id: int
    control_id: str
    status: str  # pending, passed, failed, error, skipped
    message: str | None
    evidence: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScanRead(BaseModel):
    """Schema for reading scan details."""

    id: int
    user_id: int
    m365_connection_id: int | None
    connection_name: str | None = None
    azure_connection_id: int | None
    gcp_connection_id: int | None
    aws_connection_id: int | None
    framework: str
    benchmark: str
    version: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    compliance_score: Decimal | None
    total_controls: int
    passed_count: int
    failed_count: int
    skipped_count: int
    error_count: int
    notes: str | None
    results: list[ScanResultRead] | None = None

    model_config = ConfigDict(from_attributes=True)


class ScanListItem(BaseModel):
    """Schema for scan list items (abbreviated)."""

    id: int
    user_id: int
    m365_connection_id: int | None
    connection_name: str | None = None
    framework: str
    benchmark: str
    version: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    compliance_score: Decimal | None
    total_controls: int
    passed_count: int
    failed_count: int
    skipped_count: int
    error_count: int

    model_config = ConfigDict(from_attributes=True)


class ScanCreatedResponse(BaseModel):
    """Response schema for scan creation."""

    id: int
    status: str
    message: str
