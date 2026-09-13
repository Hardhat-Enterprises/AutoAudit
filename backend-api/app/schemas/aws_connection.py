"""Pydantic schemas for AWS connections."""

from datetime import datetime

from pydantic import BaseModel, Field


class AWSConnectionBase(BaseModel):
    """Base schema for AWS connection."""

    name: str = Field(..., min_length=1, max_length=255, description="Friendly name for this connection")
    account_id: str = Field(..., min_length=12, max_length=20, description="AWS account ID (12-digit number)")
    access_key_id: str = Field(..., min_length=1, max_length=255, description="IAM access key ID")
    region: str = Field("us-east-1", min_length=1, max_length=50, description="AWS region (e.g., us-east-1)")


class AWSConnectionCreate(AWSConnectionBase):
    """Schema for creating an AWS connection."""

    secret_access_key: str = Field(..., min_length=1, description="IAM secret access key")


class AWSConnectionUpdate(BaseModel):
    """Schema for updating an AWS connection."""

    name: str | None = Field(None, min_length=1, max_length=255)
    account_id: str | None = Field(None, min_length=12, max_length=20)
    access_key_id: str | None = Field(None, min_length=1, max_length=255)
    secret_access_key: str | None = Field(None, min_length=1, description="New secret access key (if changing)")
    region: str | None = Field(None, min_length=1, max_length=50)
    is_active: bool | None = None


class AWSConnectionRead(AWSConnectionBase):
    """Schema for reading an AWS connection (without secret)."""

    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AWSConnectionTestResult(BaseModel):
    """Schema for AWS connection test result."""

    success: bool
    message: str
    account_alias: str | None = None
