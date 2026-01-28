# METADATA
# title: Ensure all forms of mail forwarding are blocked and/or disabled
# description: |
#   Transport rules that automatically forward or redirect mail to external
#   recipients pose a significant data exfiltration risk. Additionally,
#   outbound spam filter policies must have AutoForwardingMode set to Off.
#   Rules that whitelist domains by setting SCL to -1 also pose security risks.
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

import rego.v1

default result := {
    "compliant": false,
    "message": "Evaluation failed: unable to retrieve outbound spam filter policy data",
    "details": {}
}

# Main evaluation rule
result := output if {
    # Outbound policies are required
    outbound_policies := input.outbound_spam_filter_policies
    auto_forwarding_blocked := input.auto_forwarding_blocked

    # Get rules (default to empty array if missing)
    forwarding_rules := get_array(input, "forwarding_rules")
    whitelist_rules := get_array(input, "whitelist_rules")

    # Filter to only enabled rules
    enabled_forwarding_rules := [r | some r in forwarding_rules; r.state == "Enabled"]
    enabled_whitelist_rules := [r | some r in whitelist_rules; r.state == "Enabled"]

    # Find policies where AutoForwardingMode is not Off
    non_compliant_policies := [p | some p in outbound_policies; p.auto_forwarding_mode != "Off"]

    # Check all conditions - compliant only if all are true
    compliant := is_compliant(enabled_forwarding_rules, enabled_whitelist_rules, auto_forwarding_blocked)

    # Build message
    msg := build_message(enabled_forwarding_rules, enabled_whitelist_rules, non_compliant_policies, auto_forwarding_blocked)

    # Build affected resources
    affected := build_affected(enabled_forwarding_rules, enabled_whitelist_rules, non_compliant_policies)

    output := {
        "compliant": compliant,
        "message": msg,
        "affected_resources": affected,
        "details": {
            "total_transport_rules": get_number(input, "total_rules"),
            "enabled_forwarding_rules": count(enabled_forwarding_rules),
            "enabled_whitelist_rules": count(enabled_whitelist_rules),
            "forwarding_rules": enabled_forwarding_rules,
            "whitelist_rules": enabled_whitelist_rules,
            "outbound_spam_filter_policies": outbound_policies,
            "auto_forwarding_blocked": auto_forwarding_blocked
        }
    }
}

# Helper to get array with default
get_array(obj, key) := value if {
    value := obj[key]
} else := []

# Helper to get number with default
get_number(obj, key) := value if {
    value := obj[key]
} else := 0

# Helper to compute compliance - true only if all conditions met
is_compliant(fwd_rules, wl_rules, blocked) := true if {
    count(fwd_rules) == 0
    count(wl_rules) == 0
    blocked == true
} else := false

# Build message - all compliant
build_message(fwd, wl, policies, blocked) := "All forms of mail forwarding are blocked and no domain whitelist rules exist" if {
    count(fwd) == 0
    count(wl) == 0
    blocked == true
}

# Build message - has issues
build_message(fwd, wl, policies, blocked) := msg if {
    issues := array.concat(
        array.concat(
            fwd_issues(fwd),
            wl_issues(wl)
        ),
        policy_issues(policies, blocked)
    )
    count(issues) > 0
    msg := concat("; ", issues)
}

# Issue helpers
fwd_issues(rules) := [sprintf("%d enabled forwarding rule(s)", [count(rules)])] if {
    count(rules) > 0
} else := []

wl_issues(rules) := [sprintf("%d enabled whitelist rule(s) with SCL=-1", [count(rules)])] if {
    count(rules) > 0
} else := []

policy_issues(policies, blocked) := [sprintf("AutoForwardingMode not Off in %d policy(ies)", [count(policies)])] if {
    blocked == false
} else := []

# Build affected resources
build_affected(fwd, wl, policies) := resources if {
    fwd_names := [sprintf("Forwarding rule: %s", [r.name]) | some r in fwd]
    wl_names := [sprintf("Whitelist rule: %s (domains: %v)", [r.name, r.sender_domain]) | some r in wl]
    policy_names := [sprintf("Outbound policy '%s' has AutoForwardingMode=%s", [p.name, p.auto_forwarding_mode]) | some p in policies]
    resources := array.concat(array.concat(fwd_names, wl_names), policy_names)
}
