"""Input validation for security-sensitive fields.

NOTE: This validation function is duplicated in engine/powershell/service/executor.py
because the powershell service is an isolated package. Keep both copies in sync.
"""

import re

# Azure AD tenant ID: standard GUID format
_TENANT_ID_GUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# Azure AD tenant ID: verified domain name (e.g. contoso.onmicrosoft.com)
# Labels allow alphanumeric + hyphens; TLD must be alpha-only (2+ chars)
_TENANT_ID_DOMAIN_RE = re.compile(
    r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?"
    r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*"
    r"\.[a-zA-Z]{2,}$"
)


def validate_tenant_id(value: str) -> str:
    """Validate that a tenant_id is a GUID or domain name.

    This prevents PowerShell command injection by ensuring the value
    contains only characters that are structurally safe for interpolation
    into script strings.

    Args:
        value: The tenant_id to validate.

    Returns:
        The stripped, validated tenant_id.

    Raises:
        ValueError: If the value does not match GUID or domain format.
    """
    stripped = value.strip()
    if not stripped:
        raise ValueError("tenant_id must not be empty")
    if _TENANT_ID_GUID_RE.match(stripped) or _TENANT_ID_DOMAIN_RE.match(stripped):
        return stripped
    raise ValueError(
        f"Invalid tenant_id format: {stripped!r}. "
        "Must be a GUID (e.g. 12345678-1234-1234-1234-123456789abc) "
        "or a domain name (e.g. contoso.onmicrosoft.com)."
    )
