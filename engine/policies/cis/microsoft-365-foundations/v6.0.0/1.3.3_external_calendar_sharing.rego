# METADATA
# title: Ensure 'External sharing' of calendars is not available
# description: |
#   Calendar information must not be shared using sharing-policy rules that
#   apply anonymously or to any unspecified domain. This policy flags Domains
#   entries that pair Anonymous or wildcard domains with CalendarSharing
#   capabilities on enabled sharing policies.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.3.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_1_3_3

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to retrieve sharing policy data",
    "details": {},
}

result := output if {
    input.sharing_policies != null
    violations := get_array(input, "calendar_sharing_violations")
    affected := [sprintf("%s: %s", [v.policy_name, v.domain_entry]) |
        some v in violations
        v.policy_name != null
        v.domain_entry != null
    ]
    output := {
        "compliant": count(violations) == 0,
        "message": build_message(violations),
        "affected_resources": affected,
        "details": {
            "total_policies": object.get(input, "total_policies", null),
            "violating_count": count(violations),
            "violations": violations,
        },
    }
}

get_array(obj, key) := obj[key] if { obj[key] } else := []

build_message(violations) := "No enabled sharing policies allow anonymous or wildcard calendar sharing" if {
    count(violations) == 0
} else := sprintf("%d calendar sharing domain rule(s) allow anonymous or wildcard external-style sharing", [count(violations)])
