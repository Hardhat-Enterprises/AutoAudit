"""PIM role policies collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 5.3.1, 5.3.3, 5.3.4, 5.3.5

Connection Method: Microsoft Graph API
Required Scopes: RoleManagementPolicy.Read.Directory
Graph Endpoints:
    - /policies/roleManagementPolicies
    - /policies/roleManagementPolicies/{id}/rules
    - /policies/roleManagementPolicies/{id}/rules/Approval_EndUser_Assignment

Controls covered:
    - 5.3.1: Ensure 'Privileged Identity Management' is used to manage roles
    - 5.3.3: Ensure 'Access reviews' for privileged roles are configured
    - 5.3.4: Ensure approval is required for Global Administrator role activation
    - 5.3.5: Ensure approval is required for Privileged Role Administrator activation
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class PimRolePoliciesDataCollector(BaseDataCollector):
    """Collects PIM role management policies for CIS compliance evaluation.

    This collector retrieves Privileged Identity Management policies and rules
    to verify proper configuration of privileged role management.
    """

    # Role IDs for privileged roles we need to check
    GLOBAL_ADMIN_ROLE_TEMPLATE_ID = "62e90394-69f5-4237-9190-012177145e10"
    PRIVILEGED_ROLE_ADMIN_TEMPLATE_ID = "e8611ab8-c189-46e8-94e1-60213ab1f814"

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect PIM role management policy data.

        Returns:
            Dict containing:
            - role_management_policies: List of all role management policies
            - global_admin_policy: Policy for Global Administrator role with rules
            - privileged_role_admin_policy: Policy for Privileged Role Administrator with rules
            - global_admin_approval_required: Whether approval is required for GA activation
            - privileged_role_admin_approval_required: Whether approval is required for PRA activation
            - global_admin_mfa_required: Whether MFA is required for GA activation
            - global_admin_justification_required: Whether justification is required for GA
            - max_activation_duration_hours: Maximum activation duration configured
            - pim_enabled: Whether PIM is being used (policies exist)
        """
        # Step 1: Get all role management policies
        # Note: This endpoint requires beta API for full policy details
        policies_response = await client.get(
            "/policies/roleManagementPolicies",
            beta=True,
            params={"$filter": "scopeId eq '/' and scopeType eq 'DirectoryRole'"},
        )
        policies = policies_response.get("value", [])

        # Step 2: Get role definitions to map scope to role names
        role_definitions = await client.get_all_pages(
            "/roleManagement/directory/roleDefinitions",
            beta=True,
        )
        role_map = {r.get("templateId"): r for r in role_definitions}

        # Step 3: Process each policy and enrich with rules for key roles
        enriched_policies = []
        global_admin_policy = None
        privileged_role_admin_policy = None

        for policy in policies:
            policy_id = policy.get("id")
            # scopeId format: /DirectoryRoles/{roleTemplateId}
            scope_id = policy.get("scopeId", "")

            # Extract role template ID from scope
            role_template_id = None
            if scope_id.startswith("/"):
                role_template_id = scope_id.split("/")[-1] if "/" in scope_id else scope_id

            policy_data = {
                "id": policy_id,
                "scopeId": scope_id,
                "scopeType": policy.get("scopeType"),
                "roleTemplateId": role_template_id,
                "roleName": role_map.get(role_template_id, {}).get("displayName"),
            }

            # Get detailed rules for Global Admin and Privileged Role Admin
            if role_template_id in [
                self.GLOBAL_ADMIN_ROLE_TEMPLATE_ID,
                self.PRIVILEGED_ROLE_ADMIN_TEMPLATE_ID,
            ]:
                rules_response = await client.get(
                    f"/policies/roleManagementPolicies/{policy_id}/rules",
                    beta=True,
                )
                rules = rules_response.get("value", [])
                policy_data["rules"] = rules

                # Extract key settings from rules
                policy_data.update(self._extract_rule_settings(rules))

                if role_template_id == self.GLOBAL_ADMIN_ROLE_TEMPLATE_ID:
                    global_admin_policy = policy_data
                elif role_template_id == self.PRIVILEGED_ROLE_ADMIN_TEMPLATE_ID:
                    privileged_role_admin_policy = policy_data

            enriched_policies.append(policy_data)

        return {
            "role_management_policies": enriched_policies,
            "total_policies": len(policies),
            "pim_enabled": len(policies) > 0,
            "global_admin_policy": global_admin_policy,
            "privileged_role_admin_policy": privileged_role_admin_policy,
            "global_admin_approval_required": (
                global_admin_policy.get("approval_required") if global_admin_policy else None
            ),
            "privileged_role_admin_approval_required": (
                privileged_role_admin_policy.get("approval_required")
                if privileged_role_admin_policy
                else None
            ),
            "global_admin_mfa_required": (
                global_admin_policy.get("mfa_required") if global_admin_policy else None
            ),
            "global_admin_justification_required": (
                global_admin_policy.get("justification_required") if global_admin_policy else None
            ),
            "global_admin_max_activation_duration": (
                global_admin_policy.get("max_activation_duration") if global_admin_policy else None
            ),
        }

    def _extract_rule_settings(self, rules: list[dict]) -> dict[str, Any]:
        """Extract key settings from PIM policy rules.

        Args:
            rules: List of rule objects from roleManagementPolicies/{id}/rules

        Returns:
            Dict with extracted settings:
            - approval_required: bool
            - mfa_required: bool
            - justification_required: bool
            - max_activation_duration: str (ISO 8601 duration)
        """
        settings = {
            "approval_required": None,
            "mfa_required": None,
            "justification_required": None,
            "max_activation_duration": None,
        }

        for rule in rules:
            rule_type = rule.get("@odata.type", "")
            rule_id = rule.get("id", "")

            # Approval rule
            if "unifiedRoleManagementPolicyApprovalRule" in rule_type:
                if "EndUser_Assignment" in rule_id:
                    setting = rule.get("setting", {})
                    settings["approval_required"] = setting.get("isApprovalRequired", False)

            # Enablement rule (MFA and justification)
            elif "unifiedRoleManagementPolicyEnablementRule" in rule_type:
                if "EndUser_Assignment" in rule_id:
                    enabled_rules = rule.get("enabledRules", [])
                    settings["mfa_required"] = "MultiFactorAuthentication" in enabled_rules
                    settings["justification_required"] = "Justification" in enabled_rules

            # Expiration rule (max duration)
            elif "unifiedRoleManagementPolicyExpirationRule" in rule_type:
                if "EndUser_Assignment" in rule_id:
                    settings["max_activation_duration"] = rule.get("maximumDuration")

        return settings
