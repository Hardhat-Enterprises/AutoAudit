package cis.microsoft_365_foundations.v6_0_0.control_1_3_3

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to verify sharing policy settings",
    "details": {},
}

default compliant := false

sharing_policies := object.get(input, "sharing_policies", [])

non_compliant_policies := [
    {"name": policy.Name, "domains": policy.Domains, "enabled": policy.Enabled} |
    some policy in sharing_policies
    policy.Enabled == true
    some domain in policy.Domains
    allows_external(domain)
]

allows_external(domain) if {
    startswith(domain, "*:")
}

allows_external(domain) if {
    startswith(domain, "Anonymous:")
}

compliant if {
    count(sharing_policies) > 0
    count(non_compliant_policies) == 0
}

result := {
    "compliant": true,
    "message": sprintf("All %d sharing polic(ies) restrict external calendar sharing.", [count(sharing_policies)]),
    "details": {"total_policies": count(sharing_policies)},
} if {
    compliant
}

result := {
    "compliant": false,
    "message": sprintf("%d sharing polic(ies) allow external calendar sharing.", [count(non_compliant_policies)]),
    "details": {"non_compliant_policies": non_compliant_policies},
} if {
    count(sharing_policies) > 0
    count(non_compliant_policies) > 0
}

result := {
    "compliant": false,
    "message": "No sharing policies found; unable to verify.",
    "details": {},
} if {
    count(sharing_policies) == 0
}