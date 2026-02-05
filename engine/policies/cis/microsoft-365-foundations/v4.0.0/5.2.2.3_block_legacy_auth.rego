# METADATA
# title: Ensure Conditional Access policies block legacy authentication
# description: |
#   Legacy authentication protocols (IMAP, SMTP, POP3, older Office clients)
#   do not support MFA and are commonly exploited in password spray and
#   credential stuffing attacks. Block these protocols via Conditional Access.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-5.2.2.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v4.0.0
#   severity: high
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.All

package cis.microsoft_365_foundations.v4_0_0.control_5_2_2_3

default result := {"compliant": false, "message": "Evaluation failed"}

# Check if a policy blocks legacy authentication for all users/apps
is_legacy_auth_block_policy(policy) if {
    policy.state == "enabled"
    policy.targets_all_users == true
    policy.targets_all_apps == true
    policy.blocks_legacy_auth == true
    policy.grant_control == "block"
}

result := output if {
    blocking_policies := [p | some p in input.conditional_access_policies; is_legacy_auth_block_policy(p)]
    compliant := count(blocking_policies) > 0

    output := {
        "compliant": compliant,
        "message": generate_message(blocking_policies, input.conditional_access_policies),
        "affected_resources": generate_affected_resources(compliant, blocking_policies),
        "details": {
            "total_policies": count(input.conditional_access_policies),
            "legacy_auth_block_policies": count(blocking_policies),
            "blocking_policy_names": [p.display_name | some p in blocking_policies]
        }
    }
}

generate_message(blocking_policies, all_policies) := msg if {
    count(blocking_policies) > 0
    msg := sprintf("Found %d Conditional Access policy(ies) blocking legacy authentication", [count(blocking_policies)])
}

generate_message(blocking_policies, all_policies) := msg if {
    count(blocking_policies) == 0
    msg := "No Conditional Access policy found that blocks legacy authentication for all users and applications"
}

generate_affected_resources(true, _) := []
generate_affected_resources(false, _) := ["No legacy auth blocking policy configured"]
