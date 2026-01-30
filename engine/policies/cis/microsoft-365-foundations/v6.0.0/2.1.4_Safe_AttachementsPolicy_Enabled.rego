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

default result := {"compliant": false, "message": "Evaluation failed"}

safe_attachment_policies := object.get(input, "safe_attachment_policies", [])

policy_name(p) := name if {
    name := object.get(p, "Name", null)
    name != null
} else := identity if {
    identity := object.get(p, "Identity", null)
    identity != null
} else := "Unknown policy"

built_in_policies := [p |
    p := safe_attachment_policies[_]
    policy_name(p) == "Built-In Protection Policy"
]

has_policy := count(built_in_policies) > 0
policy := built_in_policies[0] if { has_policy }

policy_identity := object.get(policy, "Identity", object.get(policy, "Name", "Unknown policy"))
policy_enable := object.get(policy, "Enable", null)
policy_action := object.get(policy, "Action", null)
policy_quarantine_tag := object.get(policy, "QuarantineTag", null)

compliant if {
    has_policy
    policy_enable == true
    policy_action == "Block"
    policy_quarantine_tag == "AdminOnlyAccessPolicy"
}

result := {
    "compliant": compliant,
    "message": message,
    "affected_resources": affected_resources,
    "details": {
        "identity": policy_identity,
        "enable": policy_enable,
        "action": policy_action,
        "quarantine_tag": policy_quarantine_tag
    }
} if {
    true
}

message := "Safe Attachments Built-In Protection Policy is enabled, blocking threats, and correctly configured." if {
    compliant
} else := "Safe Attachments Built-In Protection Policy is disabled." if {
    has_policy
    policy_enable == false
} else := "Safe Attachments policy action is not set to 'Block'." if {
    has_policy
    policy_enable == true
    policy_action != "Block"
} else := "Safe Attachments policy does not use the 'AdminOnlyAccessPolicy' quarantine tag." if {
    has_policy
    policy_enable == true
    policy_action == "Block"
    policy_quarantine_tag != "AdminOnlyAccessPolicy"
} else := "Safe Attachments Built-In Protection Policy was not found." if {
    not has_policy
} else := "Unable to determine Safe Attachments policy configuration."

affected_resources := [] if {
    compliant
}

affected_resources := [
    sprintf("Non-compliant Safe Attachments policy: %v", [policy_identity])
] if {
    not compliant
    has_policy
}

affected_resources := ["Safe Attachments Built-In Protection Policy not found"] if {
    not compliant
    not has_policy
}
