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
    level: str  # Benchmark level (e.g., "L1", "L2" for CIS; varies by framework)
    is_manual: bool  # True if control has no API, always manual
    benchmark_audit_type: str  # What the benchmark says: "Automated" or "Manual"
    automation_status: str  # ready, deferred, blocked, manual, not_started
    data_collector_id: str | None = None  # Null for manual controls
    policy_file: str | None = None  # Null for manual controls
    requires_permissions: list[str] | None = None
    notes: str | None = None  # Blockers, special considerations


class AuditReadinessGap(BaseModel):
    """A benchmark control that still needs work before audit execution."""

    control_id: str
    title: str
    automation_status: str
    severity: str | None = None
    service: str | None = None
    requires_permissions: list[str] | None = None
    notes: str | None = None


class AuditReadinessSummary(BaseModel):
    """Benchmark-level audit readiness summary."""

    framework: str
    slug: str
    version: str
    benchmark: str
    total_controls: int
    audit_ready_controls: int
    gap_controls: int
    ready_controls: int
    manual_controls: int
    deferred_controls: int
    blocked_controls: int
    not_started_controls: int
    unknown_controls: int
    readiness_percentage: float
    status: str
    gaps: list[AuditReadinessGap]
