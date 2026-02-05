# METADATA
# title: Ensure 'AuditDisabled' organizationally is set to 'False'
# description: |
#   Mailbox auditing is enabled by default for all organizations. Ensure that
#   organization-wide auditing has not been explicitly disabled, as this would
#   prevent the capture of critical mailbox activities for security investigations.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-6.1.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_6_1_1

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    audit_disabled := input.audit_disabled

    # Compliant when AuditDisabled is False (auditing is enabled)
    compliant := audit_disabled == false

    output := {
        "compliant": compliant,
        "message": generate_message(audit_disabled),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "audit_disabled": audit_disabled
        }
    }
}

generate_message(audit_disabled) := msg if {
    audit_disabled == false
    msg := "Organization-wide mailbox auditing is enabled (AuditDisabled = False)"
}

generate_message(audit_disabled) := msg if {
    audit_disabled == true
    msg := "Organization-wide mailbox auditing is disabled (AuditDisabled = True)"
}

generate_message(audit_disabled) := msg if {
    audit_disabled == null
    msg := "Unable to determine AuditDisabled status"
}

generate_affected_resources(true) := []
generate_affected_resources(false) := ["Organization mailbox auditing is disabled"]
