# METADATA
# title: Ensure outbound anti-spam message limits are in place
# description: |
#   The default outbound anti-spam policy in Microsoft Defender automatically applies
#   to all users and is designed to detect and limit suspicious email-sending behavior.
#   The recommended state is:
#    • External: Restrict sending to external recipients (per hour) - 500
#    • Internal: Restrict sending to internal recipients (per hour) - 1000
#    • Daily: Maximum recipient limit per day - 1000
#    • Action: Over limit action - Restrict the user from sending mail
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.15
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_15

import rego.v1

# Expected policy values
required_policy_fields := {
    "RecipientLimitExternalPerHour": 500,
    "RecipientLimitInternalPerHour": 1000,
    "RecipientLimitPerDay": 1000,
}

valid_actions := {"BlockUser", "RestrictUser", "Restrict"}
missing_sentinel := "__missing__"

limits_compliant if input != null {
    policy := input.default_policy
    policy != null

    all_keys_correct := {k | k in required_policy_fields; policy[k] == required_policy_fields[k]}
    count(all_keys_correct) == count(required_policy_fields)

    # Action must match one of the valid options
    policy.ActionWhenThresholdReached in valid_actions
}

limits_compliant := false if {
    policy := input.default_policy
    policy != null
    some k
    required_policy_fields[k]
    object.get(policy, k, missing_sentinel) == missing_sentinel
}

limits_compliant := false if {
    policy := input.default_policy
    policy != null
    object.get(policy, "ActionWhenThresholdReached", missing_sentinel) == missing_sentinel
}

limits_compliant := false if {
    policy := input.default_policy
    policy != null
    some k
    required_policy_fields[k]
    object.get(policy, k, missing_sentinel) != missing_sentinel
    policy[k] != required_policy_fields[k]
}

limits_compliant := false if {
    policy := input.default_policy
    policy != null
    object.get(policy, "ActionWhenThresholdReached", missing_sentinel) != missing_sentinel
    not policy.ActionWhenThresholdReached in valid_actions
}

policy := input.default_policy
has_policy := policy != null

compliant := true if {
    has_policy
    limits_compliant
}

compliant := false if {
    has_policy
    not limits_compliant
}

compliant := false if {
    not has_policy
}

compliant_message := "Outbound spam filter policy is correctly configured for message limits and over-limit action"
non_compliant_message := "Outbound spam filter policy settings for message limits or over-limit action are misconfigured"
generate_message(true) := compliant_message
generate_message(false) := non_compliant_message

generate_affected_resources(true, _) := []
generate_affected_resources(false, _) := ["Outbound Spam Filter Policy"]

result := {
    "compliant": compliant,
    "message": generate_message(compliant),
    "affected_resources": generate_affected_resources(compliant, input),
    "details": {
        "RecipientLimitExternalPerHour": object.get(policy, "RecipientLimitExternalPerHour", null),
        "RecipientLimitInternalPerHour": object.get(policy, "RecipientLimitInternalPerHour", null),
        "RecipientLimitPerDay": object.get(policy, "RecipientLimitPerDay", null),
        "ActionWhenThresholdReached": object.get(policy, "ActionWhenThresholdReached", null),
        "required_policy_settings": required_policy_fields,
        "valid_actions": valid_actions
    }
}
