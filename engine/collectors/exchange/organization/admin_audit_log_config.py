"""Admin audit log config collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 3.1.1

Control Descriptions:
    3.1.1 - Ensure Microsoft 365 audit log search is Enabled

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-AdminAuditLogConfig
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class AdminAuditLogConfigDataCollector(BasePowerShellCollector):
    """Collects admin audit log config for CIS compliance evaluation.

    This collector retrieves unified audit log ingestion settings used
    by Microsoft 365 audit log search.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect admin audit log configuration data.

        Returns:
            Dict containing:
            - admin_audit_log_config: Full admin audit log configuration
            - unified_audit_log_ingestion_enabled: Unified audit log
              ingestion status (CIS 3.1.1)
        """
        config = await client.run_cmdlet("ExchangeOnline", "Get-AdminAuditLogConfig")

        return {
            "admin_audit_log_config": config,
            "unified_audit_log_ingestion_enabled": config.get(
                "UnifiedAuditLogIngestionEnabled"
            ),
        }
