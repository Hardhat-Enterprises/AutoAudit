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
    "message": "Evaluation failed: unable to determine Microsoft 365 audit log search status",
    "affected_resources": [],
    "details": {}
}

result := output if {
    enabled := object.get(input, "unified_audit_log_ingestion_enabled", null)

    enabled != null

    # Compliant when unified audit log ingestion is enabled
    compliant := enabled == true

    output := {
        "compliant": compliant,
        "message": generate_message(enabled),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "unified_audit_log_ingestion_enabled": enabled
        }
    }
}

generate_message(enabled) := msg if {
    enabled == true
    msg := "Microsoft 365 audit log search is enabled (UnifiedAuditLogIngestionEnabled is True)"
}

generate_message(enabled) := msg if {
    enabled == false
    msg := "Microsoft 365 audit log search is disabled (UnifiedAuditLogIngestionEnabled is False)"
}

generate_affected_resources(true) := []

generate_affected_resources(false) := [
    "Microsoft 365 unified audit log ingestion is disabled"
]
