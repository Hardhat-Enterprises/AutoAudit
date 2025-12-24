# METADATA
# title: Ensure all forms of mail forwarding are blocked and/or disabled
# description: |
#   Transport rules that automatically forward or redirect mail to external
#   recipients pose a significant data exfiltration risk. Ensure no transport
#   rules exist that redirect or blind copy messages externally.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-6.2.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_6_2_1

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    forwarding_rules := input.forwarding_rules

    # Filter to only enabled forwarding rules
    enabled_forwarding_rules := [r | some r in forwarding_rules; r.state == "Enabled"]

    # Compliant when no enabled forwarding rules exist
    compliant := count(enabled_forwarding_rules) == 0

    output := {
        "compliant": compliant,
        "message": generate_message(enabled_forwarding_rules),
        "affected_resources": [r.name | some r in enabled_forwarding_rules],
        "details": {
            "total_transport_rules": input.total_rules,
            "forwarding_rules_count": count(forwarding_rules),
            "enabled_forwarding_rules": count(enabled_forwarding_rules),
            "forwarding_rules": enabled_forwarding_rules
        }
    }
}

generate_message(enabled_forwarding_rules) := msg if {
    count(enabled_forwarding_rules) == 0
    msg := "No enabled transport rules forward or redirect mail externally"
}

generate_message(enabled_forwarding_rules) := msg if {
    count(enabled_forwarding_rules) > 0
    msg := sprintf("%d enabled transport rule(s) forward or redirect mail externally", [count(enabled_forwarding_rules)])
}
