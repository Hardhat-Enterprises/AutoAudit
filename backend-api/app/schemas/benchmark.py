"""Benchmark and control schemas for API responses."""

from pydantic import BaseModel


class BenchmarkRead(BaseModel):
    """Schema for benchmark data read from metadata.json files."""

    framework: str
    slug: str
    version: str
    name: str
    platform: str
    release_date: str | None = None
    source_url: str | None = None
    control_count: int


class ControlRead(BaseModel):
    """Schema for control data read from metadata.json files."""

    control_id: str
    title: str
    description: str | None = None
    severity: str | None = None
    service: str | None = None
    level: str  # CIS benchmark level: "L1" or "L2"
    is_manual: bool  # True if control has no API, always manual
    cis_audit_type: str  # What CIS says: "Automated" or "Manual"
    automation_status: str  # ready, deferred, blocked, manual, not_started
    data_collector_id: str | None = None  # Null for manual controls
    policy_file: str | None = None  # Null for manual controls
    requires_permissions: list[str] | None = None
    notes: str | None = None  # Blockers, special considerations
