"""Conditional Access policies collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.3.2, 5.2.2.1, 5.2.2.2, 5.2.2.3, 5.2.2.4, 5.2.2.5, 5.2.2.6,
            5.2.2.7, 5.2.2.8, 5.2.2.9, 5.2.2.10, 5.2.2.11, 5.2.2.12

Connection Method: Microsoft Graph API
Required Scopes: Policy.Read.All
Graph Endpoint: /identity/conditionalAccess/policies

Automation Status:
    FULLY AUTOMATABLE:
        - 5.2.2.3: Block legacy authentication (check for policy blocking legacy client types)

    REQUIRES USER INVOLVEMENT (not yet automatable):
        - 5.2.2.1: MFA for admins - requires verifying ALL admin roles are covered
        - 5.2.2.2: MFA for all users - requires verifying exclusions are legitimate
        - 5.2.2.4: Sign-in frequency for admins - requires admin role verification
        - 5.2.2.5: Phishing-resistant MFA for admins - requires admin role verification
        - 5.2.2.6: User risk policy - requires verifying policy coverage
        - 5.2.2.7: Sign-in risk policy - requires verifying policy coverage
        - 5.2.2.8: Sign-in risk blocked - requires verifying policy coverage
        - 5.2.2.9: Managed device required - requires verifying policy coverage
        - 5.2.2.10: Managed device for security info - requires verifying policy coverage
        - 5.2.2.11: Intune enrollment sign-in frequency - requires verifying policy coverage
        - 5.2.2.12: Device code flow blocked - requires verifying policy coverage
        - 1.3.2: Sign-in session policies - requires verifying policy coverage

    These controls require "compliant with review" status where exclusions and
    policy gaps are reported for manual verification. This capability is not
    yet implemented in the evaluation framework.
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class ConditionalAccessPoliciesDataCollector(BaseDataCollector):
    """Collects Conditional Access policies for CIS compliance evaluation.

    This collector retrieves all Conditional Access policies with full
    configuration details for evaluating MFA, device compliance, session
    controls, and other security requirements.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Conditional Access policy data.

        Returns:
            Dict containing:
            - policies: List of CA policies with full configuration
            - total_policies: Number of policies
            - enabled_policies: List of enabled policies
            - enabled_policies_count: Number of enabled policies
            - report_only_policies_count: Number of report-only policies
            - disabled_policies_count: Number of disabled policies
            - policies_requiring_mfa: List of policies requiring MFA
            - policies_blocking_legacy_auth: List of policies blocking legacy auth
            - policies_requiring_compliant_device: List of policies requiring device compliance

        Note: OPA can use count() to determine array lengths, so *_count
        properties are only provided for top-level policy state counts.
        """
        # Get all Conditional Access policies
        policies = await client.get_conditional_access_policies()

        # Categorize policies by state
        enabled_policies = [p for p in policies if p.get("state") == "enabled"]
        report_only_policies = [
            p for p in policies
            if p.get("state") == "enabledForReportingButNotEnforced"
        ]
        disabled_policies = [p for p in policies if p.get("state") == "disabled"]

        # Identify policies by function
        policies_requiring_mfa = []
        policies_blocking_legacy_auth = []
        policies_requiring_compliant_device = []

        for policy in enabled_policies:
            grant_controls = policy.get("grantControls") or {}
            built_in_controls = grant_controls.get("builtInControls", [])
            conditions = policy.get("conditions") or {}
            client_app_types = conditions.get("clientAppTypes", [])

            # Check for MFA requirement
            if "mfa" in built_in_controls:
                policies_requiring_mfa.append({
                    "id": policy.get("id"),
                    "displayName": policy.get("displayName"),
                    "state": policy.get("state"),
                    "conditions": conditions,
                    "grantControls": grant_controls,
                })

            # Check for legacy auth blocking
            # Legacy auth is blocked when clientAppTypes includes legacy types and action is block
            legacy_types = {"exchangeActiveSync", "other"}
            if legacy_types.intersection(set(client_app_types)):
                if "block" in built_in_controls:
                    policies_blocking_legacy_auth.append({
                        "id": policy.get("id"),
                        "displayName": policy.get("displayName"),
                        "state": policy.get("state"),
                        "conditions": conditions,
                        "grantControls": grant_controls,
                    })

            # Check for compliant device requirement
            if "compliantDevice" in built_in_controls:
                policies_requiring_compliant_device.append({
                    "id": policy.get("id"),
                    "displayName": policy.get("displayName"),
                    "state": policy.get("state"),
                    "conditions": conditions,
                    "grantControls": grant_controls,
                })

        return {
            "policies": policies,
            "total_policies": len(policies),
            "enabled_policies": enabled_policies,
            "enabled_policies_count": len(enabled_policies),
            "report_only_policies_count": len(report_only_policies),
            "disabled_policies_count": len(disabled_policies),
            "policies_requiring_mfa": policies_requiring_mfa,
            "policies_requiring_mfa_count": len(policies_requiring_mfa),
            "policies_blocking_legacy_auth": policies_blocking_legacy_auth,
            "policies_requiring_compliant_device": policies_requiring_compliant_device,
        }
