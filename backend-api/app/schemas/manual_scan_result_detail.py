"""Pydantic schemas for manual scan result detail."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ManualScanResultDetailCreate(BaseModel):
    """Schema for creating a manual scan result detail."""

    scan_result_id: int
    comment: str | None = None


class ManualScanResultDetailUpdate(BaseModel):
    """Schema for updating a manual scan result detail."""

    comment: str | None = None


class ManualScanResultDetailRead(BaseModel):
    """Schema for reading a manual scan result detail."""

    id: int
    scan_result_id: int
    user_id: int
    comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)