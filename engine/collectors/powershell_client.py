"""PowerShell client for Exchange Online, Teams, and Security & Compliance.

This module provides connectivity to Microsoft 365 PowerShell modules using
client secret authentication via MSAL access tokens. PowerShell execution
can happen either:
- Inside a Docker container (local development with Docker Desktop)
- Via HTTP to a PowerShell service (Docker Compose / production)

Supported modules:
- ExchangeOnlineManagement (Exchange Online via -AccessToken)
- ExchangeOnlineManagement (IPPSSession via -AccessToken)
- MicrosoftTeams (via -AccessTokens)

Authentication Flow:
1. Use MSAL ConfidentialClientApplication with client_id + client_secret
2. Acquire token for the appropriate scope
3. Pass token to Docker container (via env var) or HTTP service (via request body)
4. Container/service runs PowerShell cmdlet and returns JSON
"""

import json
import subprocess
from pathlib import Path
from typing import Any

import httpx
from msal import ConfidentialClientApplication


class PowerShellExecutionError(Exception):
    """Raised when PowerShell execution fails."""

    pass


class PowerShellClient:
    """Client for PowerShell-based M365 connections using Docker or HTTP service."""

    # Service-specific scopes for token acquisition
    EXCHANGE_SCOPE = "https://outlook.office365.com/.default"
    TEAMS_SCOPE = "https://api.interfaces.records.teams.microsoft.com/.default"
    COMPLIANCE_SCOPE = "https://ps.compliance.protection.outlook.com/.default"

    DOCKER_IMAGE = "autoaudit-powershell"

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        service_url: str | None = None,
    ):
        """Initialize PowerShell client.

        Args:
            tenant_id: Azure AD tenant ID
            client_id: Application (client) ID
            client_secret: Client secret for authentication
            service_url: Optional URL of PowerShell HTTP service (e.g., http://powershell-service:8001).
                         If provided, uses HTTP instead of spawning Docker containers.
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.service_url = service_url
        self._msal_app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
        )
        self._image_checked = False

    def _ensure_docker_image(self) -> None:
        """Build Docker image if it doesn't exist."""
        if self._image_checked:
            return

        # Check if Docker is available
        try:
            subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                check=True,
            )
        except FileNotFoundError:
            raise PowerShellExecutionError(
                "Docker is not installed or not in PATH.\n"
                "Install Docker from: https://docs.docker.com/get-docker/"
            )
        except subprocess.CalledProcessError as e:
            raise PowerShellExecutionError(f"Docker check failed: {e.stderr}")

        # Check if image exists
        result = subprocess.run(
            ["docker", "images", "-q", self.DOCKER_IMAGE],
            capture_output=True,
            text=True,
        )
        if not result.stdout.strip():
            print(f"Building {self.DOCKER_IMAGE} Docker image (this may take a few minutes)...")
            dockerfile_dir = Path(__file__).parent.parent / "docker" / "powershell"
            build_result = subprocess.run(
                ["docker", "build", "-t", self.DOCKER_IMAGE, str(dockerfile_dir)],
                capture_output=True,
                text=True,
            )
            if build_result.returncode != 0:
                raise PowerShellExecutionError(
                    f"Failed to build Docker image:\n{build_result.stderr}"
                )
            print(f"Docker image {self.DOCKER_IMAGE} built successfully.")

        self._image_checked = True

    async def run_cmdlet(self, module: str, cmdlet: str, **params: Any) -> dict[str, Any]:
        """Execute a PowerShell cmdlet.

        Uses HTTP service if service_url is configured, otherwise spawns Docker container.

        Args:
            module: The PowerShell module (ExchangeOnline, Teams, Compliance)
            cmdlet: The cmdlet to run (e.g., Get-OrganizationConfig)
            **params: Parameters to pass to the cmdlet

        Returns:
            Dict containing cmdlet output.
        """
        if self.service_url:
            return await self._run_via_service(module, cmdlet, params)
        else:
            return await self._run_via_docker(module, cmdlet, params)

    async def _run_via_service(
        self, module: str, cmdlet: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute cmdlet via HTTP service.

        Args:
            module: The PowerShell module
            cmdlet: The cmdlet to run
            params: Parameters for the cmdlet

        Returns:
            Dict containing cmdlet output.
        """
        # Acquire tokens
        graph_token = None
        if module == "Teams":
            # Teams needs both Graph and Teams tokens
            graph_result = self._msal_app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )
            if "access_token" not in graph_result:
                error_desc = graph_result.get("error_description", str(graph_result))
                raise RuntimeError(f"Graph token acquisition failed: {error_desc}")
            graph_token = graph_result["access_token"]

            teams_result = self._msal_app.acquire_token_for_client(
                scopes=[self.TEAMS_SCOPE]
            )
            if "access_token" not in teams_result:
                error_desc = teams_result.get("error_description", str(teams_result))
                raise RuntimeError(f"Teams token acquisition failed: {error_desc}")
            token = teams_result["access_token"]
        else:
            # Exchange and Compliance use single token
            scope = self._get_scope_for_module(module)
            result = self._msal_app.acquire_token_for_client(scopes=[scope])
            if "access_token" not in result:
                error_desc = result.get("error_description", str(result))
                raise RuntimeError(f"Token acquisition failed: {error_desc}")
            token = result["access_token"]

        # Build request payload
        payload = {
            "module": module,
            "cmdlet": cmdlet,
            "params": params,
            "tenant_id": self.tenant_id,
            "token": token,
            "graph_token": graph_token,
        }

        # Call HTTP service
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.service_url}/execute",
                json=payload,
            )
            response.raise_for_status()

        result = response.json()
        if not result.get("success"):
            raise PowerShellExecutionError(result.get("error", "Unknown error"))

        return result.get("data")

    async def _run_via_docker(
        self, module: str, cmdlet: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute cmdlet by spawning Docker container.

        Args:
            module: The PowerShell module
            cmdlet: The cmdlet to run
            params: Parameters for the cmdlet

        Returns:
            Dict containing cmdlet output.
        """
        # Ensure Docker image exists
        self._ensure_docker_image()

        # Build environment variables for tokens
        env_vars = []

        if module == "Teams":
            # Teams needs both Graph and Teams tokens
            graph_result = self._msal_app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )
            if "access_token" not in graph_result:
                error_desc = graph_result.get("error_description", str(graph_result))
                raise RuntimeError(f"Graph token acquisition failed: {error_desc}")

            teams_result = self._msal_app.acquire_token_for_client(
                scopes=[self.TEAMS_SCOPE]
            )
            if "access_token" not in teams_result:
                error_desc = teams_result.get("error_description", str(teams_result))
                raise RuntimeError(f"Teams token acquisition failed: {error_desc}")

            env_vars = [
                "-e", f"GRAPH_TOKEN={graph_result['access_token']}",
                "-e", f"TEAMS_TOKEN={teams_result['access_token']}",
            ]
        else:
            # Exchange and Compliance use single token
            scope = self._get_scope_for_module(module)
            result = self._msal_app.acquire_token_for_client(scopes=[scope])
            if "access_token" not in result:
                error_desc = result.get("error_description", str(result))
                raise RuntimeError(f"Token acquisition failed: {error_desc}")
            env_vars = ["-e", f"EXO_TOKEN={result['access_token']}"]

        # Build PowerShell script
        script = self._build_script(module, cmdlet, params)

        # Run in Docker container (pass token via env var for security)
        docker_cmd = ["docker", "run", "--rm"] + env_vars + [self.DOCKER_IMAGE, script]
        proc = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if proc.returncode != 0:
            raise PowerShellExecutionError(f"PowerShell execution failed:\n{proc.stderr}")

        # Parse JSON output
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            raise PowerShellExecutionError(
                f"Failed to parse PowerShell output as JSON:\n{proc.stdout}\nError: {e}"
            )

    def _build_script(self, module: str, cmdlet: str, params: dict[str, Any]) -> str:
        """Build the PowerShell script to execute.

        Args:
            module: The module to import and connect
            cmdlet: The cmdlet to run
            params: Parameters for the cmdlet

        Returns:
            PowerShell script as a string
        """
        # Build parameter string for cmdlet
        param_str = ""
        for key, value in params.items():
            if isinstance(value, bool):
                param_str += f" -{key}:${str(value).lower()}"
            elif isinstance(value, str):
                param_str += f' -{key} "{value}"'
            else:
                param_str += f" -{key} {value}"

        if module == "ExchangeOnline":
            return f'''
Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline -AccessToken $env:EXO_TOKEN -Organization "{self.tenant_id}" -ShowBanner:$false
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
Connect-IPPSSession -AccessToken $env:EXO_TOKEN -Organization "{self.tenant_id}" -ShowBanner:$false
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
            # Teams module uses -AccessTokens (plural) with Graph and Teams tokens
            return f'''
Import-Module MicrosoftTeams
Connect-MicrosoftTeams -AccessTokens @($env:GRAPH_TOKEN, $env:TEAMS_TOKEN) -TenantId "{self.tenant_id}"
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

    def _get_scope_for_module(self, module: str) -> str:
        """Get the appropriate scope for a PowerShell module.

        Args:
            module: The module name (ExchangeOnline, Teams, Compliance)

        Returns:
            The OAuth scope for the module.
        """
        scopes = {
            "ExchangeOnline": self.EXCHANGE_SCOPE,
            "Teams": self.TEAMS_SCOPE,
            "Compliance": self.COMPLIANCE_SCOPE,
        }
        return scopes.get(module, self.EXCHANGE_SCOPE)
