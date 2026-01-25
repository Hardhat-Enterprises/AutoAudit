# METADATA
# title: Ensure the connection filter IP allow list is not used
# description: |
#   In Microsoft 365 organizations with Exchange Online mailboxes or standalone
#   Exchange Online Protection organizations without Exchange Online mailboxes,
#   connection filtering and the default connection filter policy identify good or
#   bad source email servers by IP addresses. The key components of the default connection
#   filter policy are IP Allow List, IP Block List and Safe list.
#   The recommended state is IP Allow List empty or undefined.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.12
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_12

import rego.v1

default result := {"compliant": false, "message": "Evaluation failed"}

policies := object.get(input, "connection_filter_policies", [])

non_compliant_policies := [
    {
        "identity": object.get(p, "Identity", object.get(p, "Name", null)),
        "ip_allow_list": object.get(p, "IPAllowList", [])
    } |
    p := policies[_]
    count(object.get(p, "IPAllowList", [])) > 0
]

compliant := count(non_compliant_policies) == 0

result := {
    "compliant": compliant,
    "message": messages[compliant],
    "affected_resources": affected_resources[compliant],
    "details": {
        "policies_evaluated": count(policies),
        "non_compliant_policies": non_compliant_policies
    }
}

messages := {
    true: "IPAllowList is empty for all Exchange Online Hosted Connection Filter policies",
    false: "IPAllowList is not empty for one or more Exchange Online Hosted Connection Filter policies"
}

affected_resources := {
    true: [],
    false: ["HostedConnectionFilterPolicy"]
}
