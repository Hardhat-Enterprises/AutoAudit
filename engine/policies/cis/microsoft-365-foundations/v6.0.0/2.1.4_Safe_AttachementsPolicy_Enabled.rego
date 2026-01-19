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

compliant if {
    input.data.enable == true
    input.data.action == "Block"
    input.data.quarantine_tag == "AdminOnlyAccessPolicy"
    input.data.identity == "Built-In Protection Policy"
}

result := {
    "compliant": compliant,
    "message": message,
    "affected_resources": affected_resources,
    "details": {
        "identity": input.data.identity,
        "enable": input.data.enable,
        "action": input.data.action,
        "quarantine_tag": input.data.quarantine_tag
    }
} if {
    true
}

message := "Safe Attachments Built-In Protection Policy is enabled, blocking threats, and correctly configured." if {
    compliant
}

message := "Safe Attachments Built-In Protection Policy is disabled." if {
    input.data.enable == false
}

message := "Safe Attachments policy action is not set to 'Block'." if {
    input.data.enable == true
    input.data.action != "Block"
}

message := "Safe Attachments policy does not use the 'AdminOnlyAccessPolicy' quarantine tag." if {
    input.data.enable == true
    input.data.quarantine_tag != "AdminOnlyAccessPolicy"
}

message := "Safe Attachments policy identity is not set to 'Built-In Protection Policy'." if {
    input.data.identity != "Built-In Protection Policy"
}

message := "Unable to determine Safe Attachments policy configuration." if {
    not input.data
}

affected_resources := [] if {
    compliant
}

affected_resources := [
    sprintf("Non-compliant Safe Attachments policy: %v", [input.data.identity])
] if {
    not compliant
    input.data.identity
}

affected_resources := ["Safe Attachments policy status unknown"] if {
    not input.data.identity
}
