# METADATA
# title: Ensure multifactor authentication is enabled for all users
# description: |
#   Requires that at least one enabled Conditional Access policy enforces MFA
#   for all users across all cloud applications. Exclusions (e.g. break-glass
#   accounts) are common and legitimate, so their presence is surfaced as
#   evidence for assessor review rather than treated as an automatic fail.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# - ref: https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesspolicy
#   description: Conditional Access policies - Microsoft Graph API
# custom:
#   control_id: CIS-5.2.2.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: critical
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_2_2_2

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to retrieve Conditional Access policy data",
    "details": {},
}

targets_all_users(p) if {
    "All" in p.conditions.users.includeUsers
}

targets_all_apps(p) if {
    "All" in p.conditions.applications.includeApplications
}

qualifying_policies := [p |
    some p in input.policies_requiring_mfa
    p.state == "enabled"
    targets_all_users(p)
    targets_all_apps(p)
]

has_exclusions(p) if {
    count(object.get(p.conditions.users, "excludeUsers", [])) > 0
}

has_exclusions(p) if {
    count(object.get(p.conditions.users, "excludeGroups", [])) > 0
}

has_exclusions(p) if {
    count(object.get(p.conditions.users, "excludeRoles", [])) > 0
}

policies_with_exclusions := [p.displayName |
    some p in qualifying_policies
    has_exclusions(p)
]

result := output if {
    count(qualifying_policies) > 0

    output := {
        "compliant": true,
        "message": sprintf(
            "MFA is required for all users via %d Conditional Access policy(ies)",
            [count(qualifying_policies)],
        ),
        "details": {
            "qualifying_policy_names": [p.displayName | some p in qualifying_policies],
            "policies_with_exclusions": policies_with_exclusions,
            "exclusions_detected": count(policies_with_exclusions) > 0,
            "total_policies_requiring_mfa": count(input.policies_requiring_mfa),
        },
    }
}

result := output if {
    count(qualifying_policies) == 0

    output := {
        "compliant": false,
        "message": "No enabled Conditional Access policy requires MFA for all users across all cloud apps",
        "details": {
            "qualifying_policy_names": [],
            "policies_with_exclusions": [],
            "exclusions_detected": false,
            "total_policies_requiring_mfa": count(input.policies_requiring_mfa),
        },
    }
}
