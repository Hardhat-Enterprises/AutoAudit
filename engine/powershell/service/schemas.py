"""Pydantic schemas for PowerShell service API."""

import re
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from executor import validate_tenant_id

_GUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
_CERT_ALIAS_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_SHAREPOINT_ADMIN_URL_RE = re.compile(
    r"^https://[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?-admin\.sharepoint\.com$",
    re.IGNORECASE,
)


class ExecuteRequest(BaseModel):
    """Request to execute a PowerShell cmdlet."""

    module: Literal["ExchangeOnline", "Compliance", "Teams", "SharePointOnline"] = (
        Field(description="PowerShell module to use")
    )
    cmdlet: str = Field(
        description="PowerShell cmdlet to execute (e.g., Get-OrganizationConfig)"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters to pass to the cmdlet",
    )
    tenant_id: str = Field(description="Azure AD tenant ID (GUID or verified domain)")
    token: Optional[str] = Field(
        default=None,
        description="Access token for Exchange/Compliance/Teams",
    )
    graph_token: Optional[str] = Field(
        default=None,
        description="Graph API token (required for Teams module)",
    )
    client_id: Optional[str] = Field(
        default=None,
        description="App registration client ID (required for SharePointOnline)",
    )
    sharepoint_admin_url: Optional[str] = Field(
        default=None,
        description="SharePoint admin URL (required for SharePointOnline)",
    )
    certificate_alias: Optional[str] = Field(
        default=None,
        description="Certificate alias resolved by the service (required for SharePointOnline)",
    )

    @field_validator("tenant_id")
    @classmethod
    def check_tenant_id_format(cls, v: str) -> str:
        return validate_tenant_id(v)

    @field_validator("client_id")
    @classmethod
    def check_client_id_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        stripped = v.strip()
        if not _GUID_RE.match(stripped):
            raise ValueError(
                "Invalid client_id format. Must be a GUID "
                "(e.g. 12345678-1234-1234-1234-123456789abc)."
            )
        return stripped

    @field_validator("sharepoint_admin_url")
    @classmethod
    def check_sharepoint_admin_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        stripped = v.strip().rstrip("/")
        if not _SHAREPOINT_ADMIN_URL_RE.match(stripped):
            raise ValueError(
                "Invalid sharepoint_admin_url format. "
                "Must be https://<tenant>-admin.sharepoint.com."
            )
        return stripped

    @field_validator("certificate_alias")
    @classmethod
    def check_certificate_alias(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        stripped = v.strip()
        if not _CERT_ALIAS_RE.match(stripped):
            raise ValueError(
                "Invalid certificate_alias format. "
                "Must be an alias name (letters, digits, underscore, hyphen)."
            )
        return stripped

    @model_validator(mode="after")
    def check_module_auth_fields(self) -> "ExecuteRequest":
        if self.module == "SharePointOnline":
            missing = [
                name
                for name, value in (
                    ("client_id", self.client_id),
                    ("sharepoint_admin_url", self.sharepoint_admin_url),
                    ("certificate_alias", self.certificate_alias),
                )
                if not value
            ]
            if missing:
                raise ValueError(
                    "SharePointOnline requires " + ", ".join(missing) + "."
                )
            if self.token:
                raise ValueError("SharePointOnline must not include token.")
            if self.graph_token:
                raise ValueError("SharePointOnline must not include graph_token.")
            return self

        if not self.token:
            raise ValueError("token is required")
        if self.module == "Teams" and not self.graph_token:
            raise ValueError("Teams module requires graph_token")
        return self


class ExecuteResponse(BaseModel):
    """Response from PowerShell cmdlet execution."""

    success: bool = Field(description="Whether execution succeeded")
    data: Any = Field(default=None, description="Cmdlet output as JSON")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
