# METADATA
# title: Essential Eight - MFA required for privileged users and Microsoft 365 services
# description: |
#   Checks whether Conditional Access policies exist that require Multi-Factor
#   Authentication (MFA) for privileged users and for access to Microsoft 365
#   services, as required by the Essential Eight MFA mitigation strategy.
#
#   This control addresses the enforcement gap between the CIS MFA controls
#   (which check authentication capability and configuration) and the Essential
#   Eight requirement, which requires MFA to be applied in specific access
#   scenarios.
#
#   A compliant result requires at least one enabled Conditional Access policy
#   that: (1) requires MFA as a grant control, (2) covers privileged users or
#   all users, and (3) applies to all cloud apps (covering M365 services).
#
#   Research reference: 26T1-SEC-EG-001, 26T1-SEC-EG-003
#
# related_resources:
# - ref: https://www.cyber.gov.au/resources-business-and-government/essential-cybersecurity/essential-eight
#   description: Australian Cyber Security Centre - Essential Eight
# - ref: https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview
#   description: Microsoft Entra ID - Conditional Access overview
# - ref: https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesspolicy
#   description: Conditional Access policies - Microsoft Graph API
# custom:
#   control_id: E8-MFA-2.1
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: critical
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All
#   - RoleManagement.Read.Directory

package essential_eight.asd_essential_eight.v2025.control_e8_mfa_2_1

import rego.v1

# ---------------------------------------------------------------------------
# Default result (returned if no rule below fires successfully)
# ---------------------------------------------------------------------------

default result := {
    "compliant": false,
    "message": "Unable to evaluate MFA enforcement: no Conditional Access policy data available",
    "details": {},
}

# ---------------------------------------------------------------------------
# Helper rules
# ---------------------------------------------------------------------------

# Policies that require MFA AND cover all M365 services (all cloud apps)
# AND target all users. This is the strongest form of MFA enforcement —
# it covers privileged users implicitly and extends across the full
# Essential Eight scope.
mfa_all_users_all_apps := [p |
    some p in input.policies_requiring_mfa_for_all_users
    p.targets_all_apps == true
]

# Policies that require MFA AND cover all M365 services
# AND specifically target privileged directory roles.
# This is the minimum enforcement expected by the Essential Eight for
# the baseline (targeting privileged users specifically).
mfa_privileged_roles_all_apps := [p |
    some p in input.policies_requiring_mfa_for_privileged_roles
    p.targets_all_apps == true
]

# Combined: any policy that satisfies MFA + M365 coverage
# for either all users or privileged roles specifically.
qualifying_policies := array.concat(mfa_all_users_all_apps, mfa_privileged_roles_all_apps)

# Is there at least one qualifying policy?
has_qualifying_policy if {
    count(qualifying_policies) > 0
}

# Does any qualifying policy have broad exclusions that could undermine coverage?
# Exclusions are flagged as a warning in the details — they are not an automatic
# fail, but should be reviewed by an assessor.
policies_with_exclusions := [p |
    some p in qualifying_policies
    p.has_exclusions == true
]

# ---------------------------------------------------------------------------
# Compliance message helpers
# ---------------------------------------------------------------------------

compliant_msg := msg if {
    has_qualifying_policy
    count(policies_with_exclusions) == 0
    msg := sprintf(
        "MFA is enforced via %d Conditional Access policy(ies) covering privileged users and Microsoft 365 services with no exclusions detected",
        [count(qualifying_policies)],
    )
}

compliant_msg := msg if {
    has_qualifying_policy
    count(policies_with_exclusions) > 0
    msg := sprintf(
        "MFA is enforced via %d Conditional Access policy(ies) covering privileged users and Microsoft 365 services, but %d policy(ies) contain exclusions that should be reviewed",
        [count(qualifying_policies), count(policies_with_exclusions)],
    )
}

non_compliant_msg := "No enabled Conditional Access policy found that requires MFA for privileged users or all users and covers Microsoft 365 services (all cloud apps)" if {
    not has_qualifying_policy
}

# ---------------------------------------------------------------------------
# Main result rule
# ---------------------------------------------------------------------------

result := output if {
    # Confirm we have usable input data before evaluating
    total := input.total_policies
    enabled := input.enabled_policies_count
    has_qualifying_policy
    msg := compliant_msg

    output := {
        "compliant": true,
        "message": msg,
        "details": {
            # Policy counts for dashboard display
            "total_ca_policies": total,
            "enabled_ca_policies": enabled,
            "mfa_policies_count": input.mfa_policies_count,
            "qualifying_policies_count": count(qualifying_policies),

            # Qualifying policy names (for report evidence)
            "qualifying_policy_names": [p.display_name | some p in qualifying_policies],

            # Exclusion warning (for assessor review)
            "policies_with_exclusions": [p.display_name | some p in policies_with_exclusions],
            "exclusions_detected": count(policies_with_exclusions) > 0,

            # Evidence: privileged roles found in tenant
            "privileged_roles_in_tenant": input.privileged_roles_count,

            # All MFA policy names (supporting evidence)
            "all_mfa_policy_names": input.all_mfa_policy_names,
        },
    }
}

result := output if {
    total := input.total_policies
    enabled := input.enabled_policies_count
    not has_qualifying_policy

    output := {
        "compliant": false,
        "message": non_compliant_msg,
        "details": {
            "total_ca_policies": total,
            "enabled_ca_policies": enabled,
            "mfa_policies_count": input.mfa_policies_count,
            "qualifying_policies_count": 0,
            "qualifying_policy_names": [],
            "policies_with_exclusions": [],
            "exclusions_detected": false,
            "privileged_roles_in_tenant": input.privileged_roles_count,
            "all_mfa_policy_names": input.all_mfa_policy_names,
        },
    }
}
