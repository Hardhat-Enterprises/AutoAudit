"""Pydantic schemas for PowerShell service API."""

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class ExecuteRequest(BaseModel):
    """Request to execute a PowerShell cmdlet."""

    module: Literal["ExchangeOnline", "Compliance", "Teams"] = Field(
        description="PowerShell module to use"
    )
    cmdlet: str = Field(
        description="PowerShell cmdlet to execute (e.g., Get-OrganizationConfig)"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters to pass to the cmdlet",
    )
    tenant_id: str = Field(description="Azure AD tenant ID")
    token: str = Field(description="Access token for Exchange/Compliance")
    graph_token: Optional[str] = Field(
        default=None,
        description="Graph API token (required for Teams module)",
    )


class ExecuteResponse(BaseModel):
    """Response from PowerShell cmdlet execution."""

    success: bool = Field(description="Whether execution succeeded")
    data: Any = Field(default=None, description="Cmdlet output as JSON")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
