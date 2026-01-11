"""Transport rules collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 6.2.1, 6.2.2

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-TransportRule, Get-HostedOutboundSpamFilterPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class TransportRulesDataCollector(BasePowerShellCollector):
    """Collects transport rules for CIS compliance evaluation.

    This collector retrieves mail transport rules to check for
    mail forwarding rules and domain whitelisting configurations.
    Also retrieves outbound spam filter policies for auto-forwarding settings.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect transport rules and outbound spam filter policy data.

        Returns:
            Dict containing:
            - transport_rules: List of transport rules
            - forwarding_rules: Rules that forward mail externally
            - whitelist_rules: Rules that whitelist domains
            - outbound_spam_filter_policies: List of outbound spam filter policies
            - auto_forwarding_blocked: Whether auto-forwarding is blocked in all policies
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

        # Find rules that whitelist domains (SetSCL -1 AND SenderDomainIs set)
        # Per CIS 6.2.2: rule is non-compliant if it has BOTH properties together
        whitelist_rules = []
        for r in rules:
            # Convert SetSCL to int (may come as string from JSON)
            set_scl_raw = r.get("SetSCL")
            try:
                set_scl = int(set_scl_raw) if set_scl_raw is not None else None
            except (ValueError, TypeError):
                set_scl = None

            sender_domain = r.get("SenderDomainIs")

            # Rule is a whitelist rule if it has BOTH SetSCL = -1 AND SenderDomainIs
            if set_scl == -1 and sender_domain:
                whitelist_rules.append({
                    "name": r.get("Name"),
                    "state": r.get("State"),
                    "sender_domain": sender_domain,
                    "set_scl": set_scl,
                })

        # Get outbound spam filter policies for auto-forwarding check (CIS 6.2.1)
        spam_policies = await client.run_cmdlet(
            "ExchangeOnline", "Get-HostedOutboundSpamFilterPolicy"
        )

        # Handle None, single policy, or list
        if spam_policies is None:
            spam_policies = []
        elif isinstance(spam_policies, dict):
            spam_policies = [spam_policies]

        # Extract auto-forwarding mode from each policy
        outbound_policies = [
            {
                "name": p.get("Name"),
                "auto_forwarding_mode": p.get("AutoForwardingMode"),
            }
            for p in spam_policies
        ]

        # Check if all policies have AutoForwardingMode set to "Off"
        auto_forwarding_blocked = all(
            p.get("AutoForwardingMode") == "Off" for p in spam_policies
        ) if spam_policies else False

        return {
            "transport_rules": rules,
            "total_rules": len(rules),
            "forwarding_rules": forwarding_rules,
            "whitelist_rules": whitelist_rules,
            "outbound_spam_filter_policies": outbound_policies,
            "auto_forwarding_blocked": auto_forwarding_blocked,
        }
