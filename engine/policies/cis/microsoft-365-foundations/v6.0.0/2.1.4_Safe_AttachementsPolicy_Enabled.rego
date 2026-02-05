# METADATA
# title: Ensure Safe Attachments policy is enabled
# description: |
#   The Safe Attachments policy helps protect users from malware in email attachments
#   by scanning attachments for viruses, malware, and other malicious content.
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.4
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_4

import rego.v1

default result := {"compliant": false, "message": "Evaluation failed"}

target_policy_candidate(p) if {
    p.Identity == "Built-In Protection Policy"
}

target_policy_candidate(p) if {
    p.Name == "Built-In Protection Policy"
}

target_policies := [p |
    p := input.safe_attachment_policies[_]
    target_policy_candidate(p)
]

target_policy := target_policies[0] if count(target_policies) > 0

policy_identity := target_policy.Identity if target_policy.Identity
policy_identity := target_policy.Name if target_policy.Name

has_policy := target_policy != null

policy_matches if {
    target_policy.Enable == true
    target_policy.Action == "Block"
    target_policy.QuarantineTag == "AdminOnlyAccessPolicy"
    policy_identity == "Built-In Protection Policy"
}

compliant := true if {
    has_policy
    policy_matches
}

compliant := false if {
    has_policy
    not policy_matches
}

compliant := null if {
    not has_policy
}

result := {
    "compliant": compliant,
    "message": message,
    "affected_resources": affected_resources,
    "details": {
        "identity": policy_identity,
        "enable": target_policy.Enable,
        "action": target_policy.Action,
        "quarantine_tag": target_policy.QuarantineTag
    }
} if {
    has_policy
}

message := "Safe Attachments Built-In Protection Policy is enabled, blocking threats, and correctly configured." if compliant == true
message := "Unable to determine Safe Attachments policy configuration." if compliant == null
message := "Safe Attachments Built-In Protection Policy is disabled." if {
    compliant == false
    target_policy.Enable == false
}
message := "Safe Attachments policy action is not set to 'Block'." if {
    compliant == false
    target_policy.Enable == true
    target_policy.Action != "Block"
}
message := "Safe Attachments policy does not use the 'AdminOnlyAccessPolicy' quarantine tag." if {
    compliant == false
    target_policy.Enable == true
    target_policy.Action == "Block"
    target_policy.QuarantineTag != "AdminOnlyAccessPolicy"
}

affected_resources := [] if compliant == true
affected_resources := ["Safe Attachments policy status unknown"] if compliant == null
affected_resources := [sprintf("Non-compliant Safe Attachments policy: %v", [policy_identity])] if {
    compliant == false
    policy_identity
}
affected_resources := ["Non-compliant Safe Attachments policy: Built-In Protection Policy"] if {
    compliant == false
    not policy_identity
}

result := {
    "compliant": false,
    "message": "Unable to determine Safe Attachments policy configuration.",
    "affected_resources": ["Safe Attachments policy status unknown"],
    "details": {
        "identity": null,
        "enable": null,
        "action": null,
        "quarantine_tag": null
    }
} if {
    not has_policy
}
