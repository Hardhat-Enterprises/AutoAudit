"""Transport rules collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 6.2.1, 6.2.2

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-TransportRule
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class TransportRulesDataCollector(BasePowerShellCollector):
    """Collects transport rules for CIS compliance evaluation.

    This collector retrieves mail transport rules to check for
    mail forwarding rules and domain whitelisting configurations.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect transport rules data.

        Returns:
            Dict containing:
            - transport_rules: List of transport rules
            - forwarding_rules: Rules that forward mail externally
            - whitelist_rules: Rules that whitelist domains
        """
        rules = await client.run_cmdlet("ExchangeOnline", "Get-TransportRule")

        # Handle None, single rule, or list
        if rules is None:
            rules = []
        elif isinstance(rules, dict):
            rules = [rules]

        # Find rules that forward mail
        forwarding_rules = [
            {
                "name": r.get("Name"),
                "state": r.get("State"),
                "redirect_to": r.get("RedirectMessageTo"),
                "forward_to": r.get("BlindCopyTo"),
            }
            for r in rules
            if r.get("RedirectMessageTo") or r.get("BlindCopyTo")
        ]

        # Find rules that whitelist domains (SetSCL -1 or similar)
        whitelist_rules = [
            {
                "name": r.get("Name"),
                "state": r.get("State"),
                "sender_domain": r.get("SenderDomainIs"),
                "set_scl": r.get("SetSCL"),
            }
            for r in rules
            if r.get("SetSCL") == -1 or r.get("SenderDomainIs")
        ]

        return {
            "transport_rules": rules,
            "total_rules": len(rules),
            "forwarding_rules": forwarding_rules,
            "whitelist_rules": whitelist_rules,
        }
