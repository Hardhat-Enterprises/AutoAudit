"""Essential Eight MFA enforcement collector.

Essential Eight Control: Multi-Factor Authentication
Control ID: E8-MFA-01

Checks whether Conditional Access policies exist that require MFA for:
  - Privileged users (users assigned to administrative directory roles)
  - Access to Microsoft 365 services (all cloud apps)

This control addresses the gap identified between the CIS MFA controls
(which check authentication *capability* and *configuration*) and the
Essential Eight requirement, which checks whether MFA is *enforced* in
the appropriate access scenarios.

Research reference: 26T1-SEC-EG-001, 26T1-SEC-EG-003

Connection Method: Microsoft Graph API
Required Scopes: Policy.Read.All, RoleManagement.Read.Directory
Graph Endpoints:
  - /identity/conditionalAccess/policies
  - /directoryRoles
  - /directoryRoles/{id}/members
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient

# Well-known Microsoft 365 privileged role display names.
# These are the roles the Essential Eight considers "privileged users"
# for the purposes of MFA enforcement.
PRIVILEGED_ROLE_NAMES = {
    "Global Administrator",
    "Privileged Role Administrator",
    "Security Administrator",
    "Exchange Administrator",
    "SharePoint Administrator",
    "Teams Administrator",
    "Compliance Administrator",
    "Billing Administrator",
    "User Administrator",
    "Authentication Administrator",
    "Helpdesk Administrator",
    "Application Administrator",
    "Cloud Application Administrator",
    "Conditional Access Administrator",
    "Intune Administrator",
}

# The "All" sentinel used by Conditional Access to target all users or all apps.
CA_ALL_SENTINEL = "All"

# The Conditional Access grant control name for MFA.
MFA_GRANT_CONTROL = "mfa"


class E8MfaEnforcementDataCollector(BaseDataCollector):
    """Collects data to assess Essential Eight MFA enforcement via Conditional Access.

    Evaluates whether enabled Conditional Access policies exist that:
      1. Require MFA as a grant control
      2. Target privileged users (by role) OR all users
      3. Cover Microsoft 365 services (all cloud apps or specific M365 apps)

    This is distinct from the CIS MFA capability checks (5.2.3.x), which
    assess whether users *can* use MFA. This control checks whether MFA
    is *required* in the appropriate scenarios as defined by Essential Eight.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect Conditional Access and privileged role data.

        Returns:
            Dict containing:
            - conditional_access_policies: All CA policies (raw)
            - enabled_policies: Enabled CA policies only
            - policies_requiring_mfa: Enabled policies with MFA grant control
            - policies_requiring_mfa_for_privileged_roles: Policies that target
              directory roles AND require MFA
            - policies_requiring_mfa_for_all_users: Policies that target all
              users AND require MFA (covers privileged users implicitly)
            - policies_covering_m365: MFA policies that include all cloud apps
              or all applications (covers M365 services)
            - privileged_roles_in_tenant: Activated privileged roles found
            - privileged_roles_count: Number of active privileged roles
            - total_policies: Total number of CA policies
            - enabled_policies_count: Number of enabled policies
            - mfa_policies_count: Number of enabled MFA-requiring policies
        """
        # --- Fetch Conditional Access policies ---
        raw_policies = await client.get_conditional_access_policies()

        enabled_policies = [
            p for p in raw_policies if p.get("state") == "enabled"
        ]

        # --- Identify MFA-requiring policies ---
        # A policy requires MFA when "mfa" appears in grantControls.builtInControls
        policies_requiring_mfa = []
        for policy in enabled_policies:
            grant_controls = policy.get("grantControls") or {}
            built_in = grant_controls.get("builtInControls") or []
            if MFA_GRANT_CONTROL in built_in:
                policies_requiring_mfa.append(policy)

        # --- Split MFA policies by user scope ---
        # E8 cares about two user groups: privileged users and (at higher maturity)
        # all users accessing M365 services.
        mfa_for_privileged_roles: list[dict] = []
        mfa_for_all_users: list[dict] = []

        for policy in policies_requiring_mfa:
            conditions = policy.get("conditions") or {}
            users = conditions.get("users") or {}

            include_users = users.get("includeUsers") or []
            include_roles = users.get("includeRoles") or []
            include_groups = users.get("includeGroups") or []

            # Targets all users (implicitly includes privileged users)
            if CA_ALL_SENTINEL in include_users:
                mfa_for_all_users.append(self._summarise_policy(policy))

            # Targets specific privileged roles
            elif include_roles:
                mfa_for_privileged_roles.append(self._summarise_policy(policy))

            # Targets specific groups (e.g. "All Admins" security group)
            # We cannot resolve group members in the collector, so these are
            # surfaced in the policy summary for assessor review.
            elif include_groups:
                mfa_for_privileged_roles.append(self._summarise_policy(policy))

        # --- Identify policies that cover M365 services ---
        # The Essential Eight treats Microsoft 365 cloud services as the
        # "online services that process, store, or communicate sensitive data".
        # A policy covers M365 when it includes All cloud apps.
        mfa_covering_m365: list[dict] = []
        all_mfa_with_scope = mfa_for_all_users + mfa_for_privileged_roles

        for policy_summary in all_mfa_with_scope:
            if policy_summary.get("targets_all_apps"):
                mfa_covering_m365.append(policy_summary)

        # --- Fetch active privileged roles in this tenant ---
        # directoryRoles only returns *activated* roles (roles that have members).
        # This gives us evidence of what privileged roles exist to protect.
        try:
            directory_roles = await client.get_directory_roles()
            privileged_roles_in_tenant = [
                {
                    "id": r.get("id"),
                    "displayName": r.get("displayName"),
                    "roleTemplateId": r.get("roleTemplateId"),
                    "is_known_privileged": r.get("displayName") in PRIVILEGED_ROLE_NAMES,
                }
                for r in directory_roles
                if r.get("displayName") in PRIVILEGED_ROLE_NAMES
            ]
        except Exception:
            # Non-fatal: role data is supplementary evidence only
            privileged_roles_in_tenant = []

        return {
            # Raw / summary counts
            "total_policies": len(raw_policies),
            "enabled_policies_count": len(enabled_policies),
            "mfa_policies_count": len(policies_requiring_mfa),

            # Core assessment data for Rego policy
            "policies_requiring_mfa_for_privileged_roles": mfa_for_privileged_roles,
            "policies_requiring_mfa_for_all_users": mfa_for_all_users,
            "policies_covering_m365": mfa_covering_m365,

            # Evidence fields
            "privileged_roles_in_tenant": privileged_roles_in_tenant,
            "privileged_roles_count": len(privileged_roles_in_tenant),

            # Supporting detail (all raw MFA policies, for auditor review)
            "all_mfa_policy_names": [
                p.get("displayName") for p in policies_requiring_mfa
            ],
        }

    def _summarise_policy(self, policy: dict) -> dict:
        """Extract the fields needed for Rego evaluation from a CA policy."""
        conditions = policy.get("conditions") or {}
        users = conditions.get("users") or {}
        apps = conditions.get("applications") or {}
        grant_controls = policy.get("grantControls") or {}

        include_users = users.get("includeUsers") or []
        include_roles = users.get("includeRoles") or []
        include_groups = users.get("includeGroups") or []
        exclude_users = users.get("excludeUsers") or []
        exclude_groups = users.get("excludeGroups") or []
        exclude_roles = users.get("excludeRoles") or []
        include_apps = apps.get("includeApplications") or []

        return {
            "id": policy.get("id"),
            "display_name": policy.get("displayName"),
            "state": policy.get("state"),

            # User scope
            "targets_all_users": CA_ALL_SENTINEL in include_users,
            "include_roles": include_roles,
            "include_roles_count": len(include_roles),
            "include_groups": include_groups,
            "include_groups_count": len(include_groups),
            "targets_groups": bool(include_groups),
            "exclude_users": exclude_users,
            "exclude_groups": exclude_groups,
            "exclude_roles": exclude_roles,
            "has_exclusions": bool(exclude_users or exclude_groups or exclude_roles),

            # App scope — "All" means all cloud apps (covers M365)
            "targets_all_apps": CA_ALL_SENTINEL in include_apps,
            "include_apps": include_apps,

            # Grant control
            "requires_mfa": MFA_GRANT_CONTROL in (
                grant_controls.get("builtInControls") or []
            ),
        }
