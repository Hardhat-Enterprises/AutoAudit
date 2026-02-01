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

default result := {"compliant": false, "message": "Evaluation failed"}

policy := object.get(input, "default_policy", {})

required_policy_fields := {
  "RecipientLimitExternalPerHour": 500,
  "RecipientLimitInternalPerHour": 1000,
  "RecipientLimitPerDay": 1000,
  "ActionWhenThresholdReached": "BlockUser",
  "NotifyOutboundSpamRecipients": {"monitored@example.com"}
}

# Function to validate individual policy settings
validate_policy_setting(setting_name, setting_value) if {
  required_policy_fields[setting_name] == setting_value
}

validate_notify_outbound_spam_recipients if {
  count(policy.NotifyOutboundSpamRecipients) > 0
}

compliant if {
  # Validate that all required policy fields match
  count({
    k |
      required_policy_fields[k] == policy[k]
  }) == count(required_policy_fields)
}

compliant_message := "Outbound spam filter policy is correctly configured and meets required standards"

non_compliant_message := "Outbound spam filter policy settings are misconfigured or incomplete"

unknown_message := "Unable to determine outbound spam filter policy configuration"

generate_message(true) := compliant_message
generate_message(false) := non_compliant_message
generate_message(null) := unknown_message

generate_affected_resources(true, _) := []

generate_affected_resources(false, data_input) := [
  "Outbound Spam Filter Policy"
]

generate_affected_resources(null, _) := ["Outbound Spam Filter Policy configuration status unknown"]

result := {
  "compliant": compliant == true,
  "message": generate_message(compliant),
  "affected_resources": generate_affected_resources(compliant, input),
  "details": {
    "RecipientLimitExternalPerHour": policy.RecipientLimitExternalPerHour,
    "RecipientLimitInternalPerHour": policy.RecipientLimitInternalPerHour,
    "RecipientLimitPerDay": policy.RecipientLimitPerDay,
    "ActionWhenThresholdReached": policy.ActionWhenThresholdReached,
    "NotifyOutboundSpamRecipients": policy.NotifyOutboundSpamRecipients,
    "required_policy_settings": required_policy_fields
  }
}
