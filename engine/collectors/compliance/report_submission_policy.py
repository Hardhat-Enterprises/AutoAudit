"""Report submission policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 8.6.1

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-ReportSubmissionPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment

Note: Despite being related to security reporting, this cmdlet is in ExchangeOnline,
not in the Compliance module.
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class ReportSubmissionPolicyDataCollector(BasePowerShellCollector):
    """Collects report submission policy for CIS compliance evaluation.

    This collector retrieves user reporting settings for Microsoft Defender
    to verify security concern reporting is properly configured.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect report submission policy data.

        Returns:
            Dict containing:
            - report_submission_policy: The report submission policy
            - report_junk_to_customized_address: Custom junk reporting address
            - report_not_junk_to_customized_address: Custom not-junk reporting address
            - report_phish_to_customized_address: Custom phish reporting address
        """
        policy = await client.run_cmdlet("ExchangeOnline", "Get-ReportSubmissionPolicy")

        return {
            "report_submission_policy": policy,
            "report_junk_to_customized_address": policy.get("ReportJunkToCustomizedAddress") if policy else None,
            "report_not_junk_to_customized_address": policy.get("ReportNotJunkToCustomizedAddress") if policy else None,
            "report_phish_to_customized_address": policy.get("ReportPhishToCustomizedAddress") if policy else None,
            "enable_reported_message_to_microsoft": policy.get("EnableReportToMicrosoft") if policy else None,
        }
