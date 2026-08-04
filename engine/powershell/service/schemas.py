"""Pydantic schemas for PowerShell service API."""

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from executor import validate_tenant_id


class ExecuteRequest(BaseModel):
    """Request to execute a PowerShell cmdlet."""

    module: Literal[
        "ExchangeOnline",
        "Compliance",
        "Teams",
        "SharePoint"
    ] = Field(description="PowerShell module to use")

    cmdlet: str = Field(
        description="PowerShell cmdlet to execute"
    )

    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters to pass to the cmdlet"
    )

    tenant_id: str = Field(
        description="Azure AD tenant ID (GUID or verified domain)"
    )

    token: str = Field(
        description="Access token for Exchange/Compliance"
    )

    graph_token: Optional[str] = Field(
        default=None,
        description="Graph API token (required for Teams module)"
    )

    tenant_name: Optional[str] = Field(
        default=None,
        description="Tenant name for SharePoint (required for SharePoint module)"
    )

    sharepoint_cert_password: Optional[str] = Field(
        default=None,
        description="Certificate password for SharePoint authentication"
    )

    client_id: Optional[str] = Field(
        default=None,
        description="Client ID for SharePoint app registration"
    )

    @field_validator("tenant_id")
    @classmethod
    def check_tenant_id_format(cls, v: str) -> str:
        return validate_tenant_id(v)
    
class ExecuteResponse(BaseModel):
    """Response from PowerShell cmdlet execution."""

    success: bool = Field(description="Whether execution succeeded")
    data: Any = Field(default=None, description="Cmdlet output as JSON")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
