"""Pydantic schemas for M365 connections."""

from datetime import datetime

from pydantic import BaseModel, Field


class M365ConnectionBase(BaseModel):
    """Base schema for M365 connection."""

    name: str = Field(..., min_length=1, max_length=255, description="Friendly name for this connection")
    tenant_id: str = Field(..., min_length=1, max_length=255, description="Azure AD tenant GUID")
    client_id: str = Field(..., min_length=1, max_length=255, description="App registration client ID")


class M365ConnectionCreate(M365ConnectionBase):
    """Schema for creating an M365 connection."""

    client_secret: str = Field(..., min_length=1, description="App registration client secret")


class M365ConnectionUpdate(BaseModel):
    """Schema for updating an M365 connection."""

    name: str | None = Field(None, min_length=1, max_length=255)
    tenant_id: str | None = Field(None, min_length=1, max_length=255)
    client_id: str | None = Field(None, min_length=1, max_length=255)
    client_secret: str | None = Field(None, min_length=1, description="New client secret (if changing)")
    is_active: bool | None = None


class M365ConnectionRead(M365ConnectionBase):
    """Schema for reading an M365 connection (without secret)."""

    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class M365ConnectionTestResult(BaseModel):
    """Schema for connection test result."""

    success: bool
    message: str
    # Backwards-compatible display field (legacy)
    tenant_name: str | None = None

    # Preferred structured tenant details
    tenant_display_name: str | None = None
    default_domain: str | None = None
    verified_domains: list[str] | None = None
