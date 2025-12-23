"""B2B collaboration policy collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 5.1.6.1

Connection Method: Microsoft Graph API
Required Scopes: Policy.Read.All
Graph Endpoint: /policies/crossTenantAccessPolicy/default
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class B2BPolicyDataCollector(BaseDataCollector):
    """Collects B2B collaboration policy for CIS compliance evaluation.

    This collector retrieves B2B collaboration settings including domain
    allowlist/blocklist configuration for external collaboration.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect B2B collaboration policy data.

        Returns:
            Dict containing:
            - b2b_policy: The B2B collaboration policy configuration
            - allowed_domains: List of allowed domains (if allowlist)
            - blocked_domains: List of blocked domains (if blocklist)
            - restriction_mode: The domain restriction mode
        """
        # Get cross-tenant access policy default settings
        policy = await client.get("/policies/crossTenantAccessPolicy/default", beta=True)

        # Extract B2B collaboration settings
        b2b_collaboration = policy.get("b2bCollaborationInbound", {})
        b2b_direct_connect = policy.get("b2bDirectConnectInbound", {})

        # Get cross-tenant access policy partners for domain restrictions
        partners_response = await client.get("/policies/crossTenantAccessPolicy/partners", beta=True)
        partners = partners_response.get("value", [])

        return {
            "cross_tenant_access_policy": policy,
            "b2b_collaboration_inbound": b2b_collaboration,
            "b2b_collaboration_outbound": policy.get("b2bCollaborationOutbound", {}),
            "b2b_direct_connect_inbound": b2b_direct_connect,
            "b2b_direct_connect_outbound": policy.get("b2bDirectConnectOutbound", {}),
            "inbound_trust": policy.get("inboundTrust", {}),
            "partners": partners,
            "partners_count": len(partners),
            "is_service_provider": policy.get("isServiceProvider"),
        }
