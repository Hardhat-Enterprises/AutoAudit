"""Sharing policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.3

Connection Method: Exchange Online PowerShell (via Docker container)
Authentication: Client secret via MSAL -> access token passed to -AccessToken parameter
Required Cmdlets: Get-SharingPolicy
Required Permissions: Exchange.ManageAsApp + Exchange role assignment
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


def _normalize_domains(domains: Any) -> list[str]:
    if domains is None:
        return []
    if isinstance(domains, str):
        s = domains.strip()
        if not s:
            return []
        for sep in (";", ","):
            if sep in s:
                return [p.strip() for p in s.split(sep) if p.strip()]
        return [s]
    if isinstance(domains, list):
        out: list[str] = []
        for item in domains:
            if not isinstance(item, str):
                continue
            chunk = item.strip()
            if not chunk:
                continue
            if ";" in chunk or "," in chunk:
                sep = ";" if ";" in chunk else ","
                out.extend(p.strip() for p in chunk.split(sep) if p.strip())
            else:
                out.append(chunk)
        return out
    return []


def _calendar_external_sharing_violation(domain_entry: str) -> str | None:
    """Return a reason code for non-compliant Domains entries.

    SharingPolicy Domains are ``domain:Capability`` pairs. Only Anonymous and wildcard
    entries with CalendarSharing capabilities are flagged; named SMTP partner domains
    are not evaluated here.
    """
    if ":" not in domain_entry:
        return None
    domain_part, cap = domain_entry.split(":", 1)
    domain_part = domain_part.strip()
    cap = cap.strip()
    if not domain_part or not cap:
        return None
    if "calendarsharing" not in cap.lower():
        return None
    low = domain_part.lower()
    if low == "anonymous":
        return "anonymous_calendar_sharing"
    if low == "*":
        return "wildcard_calendar_sharing"
    return None


def _violations_for_policies(policies: list[Any]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for policy in policies:
        if not isinstance(policy, dict):
            continue
        if policy.get("Enabled") is False:
            continue
        name = policy.get("Name") or "Unknown"
        for entry in _normalize_domains(policy.get("Domains")):
            reason = _calendar_external_sharing_violation(entry)
            if reason:
                violations.append(
                    {
                        "policy_name": name,
                        "domain_entry": entry,
                        "reason": reason,
                    }
                )
    return violations


class SharingPolicyDataCollector(BasePowerShellCollector):

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        policies = await client.run_cmdlet("ExchangeOnline", "Get-SharingPolicy")

        if policies is None:
            policies = []
        elif isinstance(policies, dict):
            policies = [policies]

        default_policy = None
        if policies:
            default_policy = next(
                (p for p in policies if p.get("Default")),
                policies[0],
            )

        violations = _violations_for_policies(policies)

        return {
            "sharing_policies": policies,
            "total_policies": len(policies),
            "default_policy": default_policy,
            "calendar_sharing_violations": violations,
            "external_calendar_sharing_restricted": len(violations) == 0,
        }
