# METADATA
# title: Ensure Microsoft 365 audit log search is Enabled
# description: |
#   Microsoft 365 audit log search should be enabled to record user and
#   administrator activities across the organization. This supports
#   security monitoring, investigations, and compliance auditing.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-3.1.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Compliance
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_3_1_1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to determine Microsoft 365 audit status",
    "affected_resources": [],
    "details": {}
}

result := output if {
    audit_disabled := object.get(input, "audit_disabled", null)

    audit_disabled != null

    # Compliant when auditing is not disabled
    compliant := audit_disabled == false

    output := {
        "compliant": compliant,
        "message": generate_message(audit_disabled),
        "affected_resources": generate_affected_resources(audit_disabled),
        "details": {
            "audit_disabled": audit_disabled
        }
    }
}

generate_message(audit_disabled) := msg if {
    audit_disabled == false
    msg := "Microsoft 365 audit log search is enabled"
}

generate_message(audit_disabled) := msg if {
    audit_disabled == true
    msg := "Microsoft 365 audit log search is disabled (AuditDisabled is True)"
}

generate_affected_resources(false) := []

generate_affected_resources(true) := [
    "Microsoft 365 unified audit logging is disabled"
]