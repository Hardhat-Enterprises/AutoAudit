# METADATA
# title: Ensure 'AuditBypassEnabled' is not enabled on mailboxes
# description: |
#   Mailbox audit bypass allows specified accounts to perform actions without
#   generating audit entries. No mailboxes should have AuditBypassEnabled set
#   to True, as this creates blind spots in security monitoring.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-6.1.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_6_1_3

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    accounts_with_bypass := input.accounts_with_bypass_enabled
    bypass_count := input.bypass_count

    # Compliant when no accounts have audit bypass enabled
    compliant := bypass_count == 0

    output := {
        "compliant": compliant,
        "message": generate_message(bypass_count),
        "affected_resources": [a.Name | some a in accounts_with_bypass],
        "details": {
            "accounts_with_bypass_enabled": bypass_count,
            "bypassed_accounts": [a.Name | some a in accounts_with_bypass]
        }
    }
}

generate_message(bypass_count) := msg if {
    bypass_count == 0
    msg := "No accounts have mailbox audit bypass enabled"
}

generate_message(bypass_count) := msg if {
    bypass_count > 0
    msg := sprintf("%d account(s) have mailbox audit bypass enabled", [bypass_count])
}
