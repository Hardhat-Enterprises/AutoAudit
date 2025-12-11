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
    data_collector_id: str
    policy_file: str
    requires_permissions: list[str] | None = None
