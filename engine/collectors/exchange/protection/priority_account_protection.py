"""Priority account strict protection policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.4.2

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-ATPProtectionPolicyRule, Get-EOPProtectionPolicyRule
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient

STRICT_PRESET_IDENTITY = "Strict Preset Security Policy"


class PriorityAccountStrictProtectionDataCollector(BasePowerShellCollector):
    """Collects the Strict Preset Security Policy rules (ATP + EOP) for CIS 2.4.2.

    Retrieves the Defender for Office 365 (ATP) and Exchange Online Protection
    (EOP) protection policy rules, isolates the built-in "Strict Preset
    Security Policy" rule from each, and extracts the fields needed to
    evaluate whether the strict preset is enabled and scoped to specific
    recipients (priority accounts/groups), per the CIS 2.4.2 audit steps.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        raw_atp_rules: Any = await client.run_cmdlet("ExchangeOnline", "Get-ATPProtectionPolicyRule")
        raw_eop_rules: Any = await client.run_cmdlet("ExchangeOnline", "Get-EOPProtectionPolicyRule")

        atp_rules = _as_list(raw_atp_rules)
        eop_rules = _as_list(raw_eop_rules)

        atp_strict_rule = _find_strict_rule(atp_rules)
        eop_strict_rule = _find_strict_rule(eop_rules)

        return {
            "atp_strict_rule_found": atp_strict_rule is not None,
            "atp_strict_rule_state": atp_strict_rule.get("State") if atp_strict_rule else None,
            "atp_strict_rule_sent_to": _non_empty(atp_strict_rule, "SentTo"),
            "atp_strict_rule_sent_to_member_of": _non_empty(atp_strict_rule, "SentToMemberOf"),
            "atp_strict_rule_recipient_domain_is": _non_empty(atp_strict_rule, "RecipientDomainIs"),
            "eop_strict_rule_found": eop_strict_rule is not None,
            "eop_strict_rule_state": eop_strict_rule.get("State") if eop_strict_rule else None,
            "eop_strict_rule_sent_to": _non_empty(eop_strict_rule, "SentTo"),
            "eop_strict_rule_sent_to_member_of": _non_empty(eop_strict_rule, "SentToMemberOf"),
            "eop_strict_rule_recipient_domain_is": _non_empty(eop_strict_rule, "RecipientDomainIs"),
        }


def _as_list(raw: Any) -> list[dict[str, Any]]:
    """Normalise a PowerShell cmdlet result to a list of dicts.

    A single matching object comes back as a bare dict rather than a
    one-item list, and no matches at all can come back as None.
    """
    if raw is None:
        return []
    if isinstance(raw, dict):
        return [raw]
    return raw


def _find_strict_rule(rules: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the rule whose Identity is the built-in strict preset, if present."""
    return next((r for r in rules if r.get("Identity") == STRICT_PRESET_IDENTITY), None)


def _non_empty(rule: dict[str, Any] | None, field: str) -> list[Any]:
    """Normalise a recipient-target field (SentTo/SentToMemberOf/RecipientDomainIs) to a list.

    These fields come back as None when unset, a bare value when a single
    entry is set, or a list when multiple entries are set.
    """
    if not rule:
        return []
    value = rule.get(field)
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]