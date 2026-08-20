"""PowerShell command executor."""

import json
import os
import re
import subprocess
from typing import Any, Dict, Optional

# NOTE: This validation function is duplicated in engine/worker/validators.py
# because the powershell service is an isolated package. Keep both copies in sync.

_TENANT_ID_GUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# Labels allow alphanumeric + hyphens; TLD must be alpha-only (2+ chars)
_TENANT_ID_DOMAIN_RE = re.compile(
    r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?"
    r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*"
    r"\.[a-zA-Z]{2,}$"
)


def validate_tenant_id(value: str) -> str:
    """Validate that a tenant_id is a GUID or domain name.

    Prevents PowerShell command injection by ensuring the value contains
    only characters that are structurally safe for interpolation.
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


class PowerShellExecutionError(Exception):
    """Raised when PowerShell execution fails."""

    pass


def build_param_string(params: Dict[str, Any]) -> str:
    """Build PowerShell parameter string from dict.

    Args:
        params: Dictionary of parameter names to values

    Returns:
        PowerShell parameter string (e.g., ' -Name "value" -Enabled:$true')
    """
    param_str = ""
    for key, value in params.items():
        if isinstance(value, bool):
            param_str += f" -{key}:${str(value).lower()}"
        elif isinstance(value, str):
            # Escape double quotes in string values
            escaped = value.replace('"', '`"')
            param_str += f' -{key} "{escaped}"'
        else:
            param_str += f" -{key} {value}"
    return param_str


def resolve_sharepoint_certificate(alias: str) -> tuple[str, str]:
    """Resolve a certificate alias to mounted PFX and password file paths.

    Alias mapping comes from the SHAREPOINT_CERT_ALIASES environment variable
    (JSON object). Request bodies never supply filesystem paths or secrets.
    """
    raw = os.environ.get("SHAREPOINT_CERT_ALIASES")
    if not raw or not raw.strip():
        raise ValueError("SHAREPOINT_CERT_ALIASES is not configured")

    try:
        mapping = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("SHAREPOINT_CERT_ALIASES is not valid JSON") from None

    if not isinstance(mapping, dict):
        raise ValueError("SHAREPOINT_CERT_ALIASES must be a JSON object")

    entry = mapping.get(alias)
    if not isinstance(entry, dict):
        raise ValueError("Unknown certificate alias")

    cert_path = entry.get("path")
    password_file = entry.get("password_file")
    if not isinstance(cert_path, str) or not cert_path.strip():
        raise ValueError("Unknown certificate alias")
    if not isinstance(password_file, str) or not password_file.strip():
        raise ValueError("Unknown certificate alias")

    cert_path = cert_path.strip()
    password_file = password_file.strip()
    if not os.path.isfile(cert_path) or not os.path.isfile(password_file):
        raise ValueError(
            "SharePoint certificate is not available for the requested alias"
        )

    return cert_path, password_file


def build_script(
    module: str,
    cmdlet: str,
    params: Dict[str, Any],
    tenant_id: str,
    client_id: Optional[str] = None,
    sharepoint_admin_url: Optional[str] = None,
) -> str:
    """Build the PowerShell script to execute.

    Args:
        module: The module to use (ExchangeOnline, Compliance, Teams, SharePointOnline)
        cmdlet: The cmdlet to run
        params: Parameters for the cmdlet
        tenant_id: Azure AD tenant ID
        client_id: App registration client ID (SharePointOnline)
        sharepoint_admin_url: SharePoint admin URL (SharePointOnline)

    Returns:
        PowerShell script as a string
    """
    tenant_id = validate_tenant_id(tenant_id)
    param_str = build_param_string(params)

    if module == "ExchangeOnline":
        return f"""
Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline -AccessToken $env:EXO_TOKEN -Organization "{tenant_id}" -ShowBanner:$false
try {{
    $result = {cmdlet}{param_str}
    if ($null -eq $result) {{
        Write-Output 'null'
    }} else {{
        $result | ConvertTo-Json -Depth 10
    }}
}} finally {{
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
}}
"""
    elif module == "Compliance":
        return f"""
Import-Module ExchangeOnlineManagement
Connect-IPPSSession -AccessToken $env:EXO_TOKEN -Organization "{tenant_id}" -ShowBanner:$false
try {{
    $result = {cmdlet}{param_str}
    if ($null -eq $result) {{
        Write-Output 'null'
    }} else {{
        $result | ConvertTo-Json -Depth 10
    }}
}} finally {{
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
}}
"""
    elif module == "Teams":
        return f"""
Import-Module MicrosoftTeams
Connect-MicrosoftTeams -AccessTokens @($env:GRAPH_TOKEN, $env:TEAMS_TOKEN) -TenantId "{tenant_id}"
try {{
    $result = {cmdlet}{param_str}
    if ($null -eq $result) {{
        Write-Output 'null'
    }} else {{
        $result | ConvertTo-Json -Depth 10
    }}
}} finally {{
    Disconnect-MicrosoftTeams -ErrorAction SilentlyContinue
}}
"""
    elif module == "SharePointOnline":
        if not client_id or not sharepoint_admin_url:
            raise ValueError(
                "SharePointOnline requires client_id and sharepoint_admin_url"
            )
        if not _TENANT_ID_GUID_RE.match(client_id):
            raise ValueError("Invalid client_id format")
        return f"""
Import-Module PnP.PowerShell
$pwd = ConvertTo-SecureString (Get-Content -Raw $env:SPO_CERT_PASSWORD_FILE).Trim() -AsPlainText -Force
Connect-PnPOnline -Url "{sharepoint_admin_url}" -ClientId "{client_id}" -Tenant "{tenant_id}" -CertificatePath $env:SPO_CERT_PATH -CertificatePassword $pwd
try {{
    $result = {cmdlet}{param_str}
    if ($null -eq $result) {{
        Write-Output 'null'
    }} else {{
        $result | ConvertTo-Json -Depth 10
    }}
}} finally {{
    Disconnect-PnPOnline
}}
"""
    else:
        raise ValueError(f"Unsupported module: {module}")


def execute_cmdlet(
    module: str,
    cmdlet: str,
    params: Dict[str, Any],
    tenant_id: str,
    token: Optional[str] = None,
    graph_token: Optional[str] = None,
    client_id: Optional[str] = None,
    sharepoint_admin_url: Optional[str] = None,
    certificate_alias: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute a PowerShell cmdlet and return the result.

    Args:
        module: PowerShell module (ExchangeOnline, Compliance, Teams, SharePointOnline)
        cmdlet: The cmdlet to run
        params: Parameters for the cmdlet
        tenant_id: Azure AD tenant ID
        token: Access token for Exchange/Compliance/Teams
        graph_token: Graph API token (required for Teams)
        client_id: App registration client ID (SharePointOnline)
        sharepoint_admin_url: SharePoint admin URL (SharePointOnline)
        certificate_alias: Certificate alias resolved from SHAREPOINT_CERT_ALIASES

    Returns:
        Parsed JSON output from the cmdlet

    Raises:
        PowerShellExecutionError: If execution fails
        ValueError: If required module fields are missing
    """
    if module == "Teams" and not graph_token:
        raise ValueError("Teams module requires graph_token")
    if module in ("ExchangeOnline", "Compliance", "Teams") and not token:
        raise ValueError("token is required")

    env = os.environ.copy()
    if module == "SharePointOnline":
        if not certificate_alias:
            raise ValueError("SharePointOnline requires certificate_alias")
        cert_path, password_file = resolve_sharepoint_certificate(certificate_alias)
        env["SPO_CERT_PATH"] = cert_path
        env["SPO_CERT_PASSWORD_FILE"] = password_file
        script = build_script(
            module,
            cmdlet,
            params,
            tenant_id,
            client_id=client_id,
            sharepoint_admin_url=sharepoint_admin_url,
        )
    else:
        script = build_script(module, cmdlet, params, tenant_id)
        if module == "Teams":
            env["GRAPH_TOKEN"] = graph_token
            env["TEAMS_TOKEN"] = token
        else:
            env["EXO_TOKEN"] = token

    # Execute PowerShell
    try:
        proc = subprocess.run(
            ["pwsh", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
    except subprocess.TimeoutExpired:
        raise PowerShellExecutionError(
            "PowerShell execution timed out after 120 seconds"
        )
    except Exception as e:
        raise PowerShellExecutionError(f"Failed to execute PowerShell: {e}")

    if proc.returncode != 0:
        raise PowerShellExecutionError(f"PowerShell execution failed:\n{proc.stderr}")

    # Parse JSON output
    stdout = proc.stdout.strip()
    if not stdout or stdout == "null":
        return None

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as e:
        raise PowerShellExecutionError(
            f"Failed to parse PowerShell output as JSON:\n{stdout}\nError: {e}"
        )
