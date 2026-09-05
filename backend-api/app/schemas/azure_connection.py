"""Pydantic schemas for Azure connections."""

from datetime import datetime

from pydantic import BaseModel, Field


class AzureConnectionBase(BaseModel):
    """Base schema for Azure connection."""

    name: str = Field(..., min_length=1, max_length=255, description="Friendly name for this connection")
    tenant_id: str = Field(..., min_length=1, max_length=255, description="Azure AD tenant GUID")
    client_id: str = Field(..., min_length=1, max_length=255, description="App registration client ID")
    subscription_id: str = Field(..., min_length=1, max_length=255, description="Azure subscription ID")


class AzureConnectionCreate(AzureConnectionBase):
    """Schema for creating an Azure connection."""

    client_secret: str = Field(..., min_length=1, description="App registration client secret")


class AzureConnectionUpdate(BaseModel):
    """Schema for updating an Azure connection."""

    name: str | None = Field(None, min_length=1, max_length=255)
    tenant_id: str | None = Field(None, min_length=1, max_length=255)
    client_id: str | None = Field(None, min_length=1, max_length=255)
    client_secret: str | None = Field(None, min_length=1, description="New client secret (if changing)")
    subscription_id: str | None = Field(None, min_length=1, max_length=255)
    is_active: bool | None = None


class AzureConnectionRead(AzureConnectionBase):
    """Schema for reading an Azure connection (without secret)."""

    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AzureConnectionTestResult(BaseModel):
    """Schema for Azure connection test result."""

    success: bool
    message: str
    tenant_display_name: str | None = None
