"""Admin audit log config collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 3.1.1

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-AdminAuditLogConfig
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class AdminAuditLogConfigDataCollector(BasePowerShellCollector):
    """Collects admin audit log configuration for CIS compliance evaluation.

    This collector retrieves unified audit log ingestion status
    to verify audit logging is properly enabled.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect admin audit log config data.

        Returns:
            Dict containing:
            - admin_audit_log_config: The full admin audit log configuration
            - unified_audit_log_ingestion_enabled: UAL ingestion status (key for CIS 3.1.1)
        """
        config = await client.run_cmdlet("ExchangeOnline", "Get-AdminAuditLogConfig")

        return {
            "admin_audit_log_config": config,
            "unified_audit_log_ingestion_enabled": config.get("UnifiedAuditLogIngestionEnabled"),
        }
