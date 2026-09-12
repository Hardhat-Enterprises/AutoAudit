# METADATA
# title: Ensure the device code sign-in flow is blocked
# description: |
#   Requires that at least one enabled Conditional Access policy blocks the
#   device code authentication flow, which is commonly abused in phishing
#   attacks that trick users into approving sign-ins on attacker-controlled
#   devices.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# - ref: https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessauthenticationflows
#   description: Conditional Access authentication flows - Microsoft Graph API
# custom:
#   control_id: CIS-5.2.2.12
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_5_2_2_12

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to retrieve Conditional Access policy data",
    "details": {},
}

# `authenticationFlows` is a newer Conditional Access condition and is only
# present in the raw policy object returned by Graph; it is not pre-flattened
# by the collector, so this reads straight off `input.policies`.
blocks_device_code_flow(p) if {
    p.state == "enabled"
    p.conditions.authenticationFlows.transferMethods == "deviceCodeFlow"
    "block" in p.grantControls.builtInControls
}

qualifying_policies := [p |
    some p in input.policies
    blocks_device_code_flow(p)
]

result := output if {
    count(qualifying_policies) > 0

    output := {
        "compliant": true,
        "message": sprintf(
            "Device code sign-in flow is blocked via %d Conditional Access policy(ies)",
            [count(qualifying_policies)],
        ),
        "details": {
            "qualifying_policy_names": [p.displayName | some p in qualifying_policies],
            "total_policies": count(input.policies),
        },
    }
}

result := output if {
    count(qualifying_policies) == 0

    output := {
        "compliant": false,
        "message": "No enabled Conditional Access policy blocks the device code sign-in flow",
        "details": {
            "qualifying_policy_names": [],
            "total_policies": count(input.policies),
        },
    }
}
