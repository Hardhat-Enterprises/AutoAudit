"""Pydantic schemas for per-user settings."""

from datetime import datetime

from pydantic import BaseModel


class UserSettingsRead(BaseModel):
    """Schema for reading user settings."""

    id: int
    user_id: int
    confirm_delete_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings."""

    confirm_delete_enabled: bool | None = None

