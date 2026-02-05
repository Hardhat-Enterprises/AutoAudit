"""Activity timeout policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.2

Connection Method: Microsoft Graph API
Required Scopes: Policy.Read.All
Graph Endpoint: /policies/activityBasedTimeoutPolicies
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class ActivityTimeoutPolicyDataCollector(BaseDataCollector):
    """Collects activity-based timeout policy for CIS compliance evaluation.

    This collector retrieves idle session timeout configuration settings
    for compliance with session management requirements.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect activity timeout policy data.

        Returns:
            Dict containing:
            - timeout_policies: List of activity-based timeout policies
            - has_timeout_policy: Whether a timeout policy is configured
        """
        # Get activity-based timeout policies
        policies = await client.get_all_pages(
            "/policies/activityBasedTimeoutPolicies",
        )

        # Parse the policy definition to extract timeout values
        timeout_settings = []
        for policy in policies:
            definition = policy.get("definition", [])
            if definition:
                # Definition is a JSON string array
                import json
                for def_str in definition:
                    try:
                        parsed = json.loads(def_str)
                        timeout_settings.append(parsed)
                    except (json.JSONDecodeError, TypeError):
                        pass

        return {
            "timeout_policies": policies,
            "total_policies": len(policies),
            "has_timeout_policy": len(policies) > 0,
            "timeout_settings": timeout_settings,
        }
