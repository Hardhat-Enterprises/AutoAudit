# METADATA
# title: Ensure a managed device is required for authentication
# description: |
#   Requires that at least one enabled Conditional Access policy requires a
#   compliant (managed) device as a grant control for all users across all
#   cloud applications.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# - ref: https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessgrantcontrols
#   description: Conditional Access grant controls - Microsoft Graph API
# custom:
#   control_id: CIS-5.2.2.9
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_2_2_9

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
    some p in input.policies_requiring_compliant_device
    p.state == "enabled"
    targets_all_users(p)
    targets_all_apps(p)
]

result := output if {
    count(qualifying_policies) > 0

    output := {
        "compliant": true,
        "message": sprintf(
            "A managed (compliant) device is required for authentication via %d Conditional Access policy(ies)",
            [count(qualifying_policies)],
        ),
        "details": {
            "qualifying_policy_names": [p.displayName | some p in qualifying_policies],
            "total_policies_requiring_compliant_device": count(input.policies_requiring_compliant_device),
        },
    }
}

result := output if {
    count(qualifying_policies) == 0

    output := {
        "compliant": false,
        "message": "No enabled Conditional Access policy requires a compliant device for all users across all cloud apps",
        "details": {
            "qualifying_policy_names": [],
            "total_policies_requiring_compliant_device": count(input.policies_requiring_compliant_device),
        },
    }
}
