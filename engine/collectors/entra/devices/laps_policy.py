"""Entra LAPS policy collector.

CIS Microsoft 365 Foundations Benchmark Control:
    v6.0.0: 5.1.4.5

Purpose:
    Retrieve Entra (Azure AD) LAPS configuration from device registration policy
    to determine whether LAPS is enabled and how it is configured.

Notes:
    - Uses Microsoft Graph beta (policy surface is in beta for some tenants).
    - Requires Policy.Read.All.
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class LapsPolicyDataCollector(BaseDataCollector):
    """Collects Entra LAPS configuration."""

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect LAPS-related settings from device registration policy."""
        policy = await client.get("/policies/deviceRegistrationPolicy", beta=True)

        custom = policy.get("customRules") or []
        local_admin = policy.get("localAdminPassword") or {}

        return {
            "raw": policy,
            "is_laps_enabled": local_admin.get("isEnabled"),
            "password_rotation_days": local_admin.get("passwordRotationInDays"),
            "password_length": local_admin.get("passwordLength"),
            "password_complexity": local_admin.get("passwordComplexity"),
            "custom_rules": custom,
        }
