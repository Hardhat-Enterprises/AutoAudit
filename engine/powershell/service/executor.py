"""PowerShell command executor."""

import json
import os
import subprocess
from typing import Any, Dict, Optional


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


def build_script(
    module: str,
    cmdlet: str,
    params: Dict[str, Any],
    tenant_id: str,
) -> str:
    """Build the PowerShell script to execute.

    Args:
        module: The module to use (ExchangeOnline, Compliance, Teams)
        cmdlet: The cmdlet to run
        params: Parameters for the cmdlet
        tenant_id: Azure AD tenant ID

    Returns:
        PowerShell script as a string
    """
    param_str = build_param_string(params)

    if module == "ExchangeOnline":
        return f'''
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
'''
    elif module == "Compliance":
        return f'''
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
'''
    elif module == "Teams":
        return f'''
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
'''
    else:
        raise ValueError(f"Unsupported module: {module}")


def execute_cmdlet(
    module: str,
    cmdlet: str,
    params: Dict[str, Any],
    tenant_id: str,
    token: str,
    graph_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute a PowerShell cmdlet and return the result.

    Args:
        module: PowerShell module (ExchangeOnline, Compliance, Teams)
        cmdlet: The cmdlet to run
        params: Parameters for the cmdlet
        tenant_id: Azure AD tenant ID
        token: Access token for Exchange/Compliance
        graph_token: Graph API token (required for Teams)

    Returns:
        Parsed JSON output from the cmdlet

    Raises:
        PowerShellExecutionError: If execution fails
        ValueError: If Teams module requested without graph_token
    """
    if module == "Teams" and not graph_token:
        raise ValueError("Teams module requires graph_token")

    # Build the script
    script = build_script(module, cmdlet, params, tenant_id)

    # Set up environment with tokens
    env = os.environ.copy()
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
        raise PowerShellExecutionError("PowerShell execution timed out after 120 seconds")
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
