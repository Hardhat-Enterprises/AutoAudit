"""Activity-based timeout policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.2

Control Description:
    1.3.2 - Ensure 'Idle session timeout' is set to '3 hours (or less)'
            for unmanaged devices

Connection Method: Microsoft Graph API
Required Scopes: Policy.Read.All
Graph Endpoint: /policies/activityBasedTimeoutPolicies
"""

import json
from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class ActivityBasedTimeoutDataCollector(BaseDataCollector):
    """Collects ActivityBasedTimeoutPolicy for CIS 1.3.2 evaluation.

    This collector retrieves the organization's idle session timeout
    configuration. The timeout value is embedded inside each policy's
    definition JSON under ActivityBasedTimeoutPolicy.ApplicationPolicies.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect activity-based timeout policy data.

        Returns:
            Dict containing:
            - activity_based_timeout_policies: Parsed list of policies
            - idle_timeout_minutes: Effective timeout for the org default
            - total_policies: Count of policies returned
        """
        raw_policies = await client.get_activity_based_timeout_policies()

        parsed_policies = []
        default_timeout_minutes = None

        for policy in raw_policies:
            definition = policy.get("definition", [])
            timeout_minutes = self._extract_idle_timeout(definition)

            parsed = {
                "id": policy.get("id"),
                "display_name": policy.get("displayName"),
                "is_organization_default": policy.get("isOrganizationDefault", False),
                "idle_timeout_minutes": timeout_minutes,
            }
            parsed_policies.append(parsed)

            if parsed["is_organization_default"]:
                default_timeout_minutes = timeout_minutes

        # Fallback: if no policy is marked as org default, use the first one
        if default_timeout_minutes is None and parsed_policies:
            default_timeout_minutes = parsed_policies[0]["idle_timeout_minutes"]

        return {
            "activity_based_timeout_policies": parsed_policies,
            "idle_timeout_minutes": default_timeout_minutes,
            "total_policies": len(parsed_policies),
        }

    @staticmethod
    def _extract_idle_timeout(definition: list) -> Any:
        """Extract WebSessionIdleTimeout in minutes from policy definition.

        The definition is a list containing a JSON-encoded string.
        Value format is 'hh:mm:ss' (e.g. '03:00:00' for 3 hours).
        """
        if not definition:
            return None

        for entry in definition:
            try:
                data = json.loads(entry) if isinstance(entry, str) else entry
            except (json.JSONDecodeError, TypeError):
                continue

            app_policies = (
                data.get("ActivityBasedTimeoutPolicy", {})
                    .get("ApplicationPolicies", [])
            )
            for app in app_policies:
                timeout = app.get("WebSessionIdleTimeout")
                if timeout:
                    return _parse_hhmmss_to_minutes(timeout)

        return None


def _parse_hhmmss_to_minutes(value: str) -> float:
    """Convert 'hh:mm:ss' string to minutes.

    Examples:
        '03:00:00' -> 180
        '01:30:00' -> 90
        '00:30:00' -> 30
    """
    if not value:
        return None

    parts = value.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
        return hours * 60 + minutes + seconds / 60
    elif len(parts) == 2:
        minutes, seconds = int(parts[0]), int(parts[1])
        return minutes + seconds / 60

    return None