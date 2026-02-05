"""Admin consent request policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 5.1.5.2

Connection Method: Microsoft Graph API
Required Scopes: Policy.Read.All
Graph Endpoint: /policies/adminConsentRequestPolicy
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class AdminConsentRequestPolicyDataCollector(BaseDataCollector):
    """Collects admin consent workflow settings for CIS compliance evaluation.

    This collector retrieves the admin consent request policy configuration
    to verify admin consent workflow is properly configured.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect admin consent request policy data.

        Returns:
            Dict containing:
            - admin_consent_policy: The admin consent request policy
            - is_enabled: Whether admin consent workflow is enabled
            - reviewers: List of designated reviewers
        """
        # Get admin consent request policy
        policy = await client.get("/policies/adminConsentRequestPolicy", beta=True)

        # Extract reviewer information
        reviewers = policy.get("reviewers", [])

        return {
            "admin_consent_policy": policy,
            "is_enabled": policy.get("isEnabled"),
            "notify_reviewers": policy.get("notifyReviewers"),
            "reminders_enabled": policy.get("remindersEnabled"),
            "request_duration_in_days": policy.get("requestDurationInDays"),
            "reviewers": reviewers,
            "reviewers_count": len(reviewers),
        }
