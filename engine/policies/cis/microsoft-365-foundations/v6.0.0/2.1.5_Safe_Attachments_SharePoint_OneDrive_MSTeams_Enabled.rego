# METADATA
# title: Ensure Safe Attachments for SharePoint, OneDrive, and Microsoft Teams is Enabled
# description: |
#   Safe Attachments for SharePoint, OneDrive, and Microsoft Teams scans these services for malicious files.
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.5
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_5

import rego.v1

default result := {"compliant": false, "message": "Evaluation failed"}

required_values := {
    "EnableATPForSPOTeamsODB": true,
    "EnableSafeDocs": true,
    "AllowSafeDocsOpen": false
}

missing_sentinel := "__missing__"

field_non_compliant(p, f) if {
    object.get(p, f, missing_sentinel) == missing_sentinel
}

field_non_compliant(p, f) if {
    object.get(p, f, missing_sentinel) != missing_sentinel
    p[f] != required_values[f]
}

policy_compliant(p) if {
    invalid_fields := {f |
        some f
        required_values[f] = _
        field_non_compliant(p, f)
    }
    count(invalid_fields) == 0
}

policy := input.atp_policy
policies := [policy] if policy != null
policies := [] if policy == null

non_compliant_policies := [ {"policy": p.Name, "failed_fields": [f |
    some f
    required_values[f] = _
    field_non_compliant(p, f)
]} |
    p := policies[_]
    not policy_compliant(p)
]

result := {
    "compliant": true,
    "message": sprintf("All %d Safe Attachments policies are compliant", [count(policies)])
} if {
    count(policies) > 0
    count(non_compliant_policies) == 0
}

result := {
    "compliant": false,
    "message": sprintf("Non-compliant policies detected: %v", [non_compliant_policies])
} if {
    count(non_compliant_policies) > 0
}

result := {
    "compliant": false,
    "message": "No Safe Attachments policies found"
} if {
    count(policies) == 0
}
