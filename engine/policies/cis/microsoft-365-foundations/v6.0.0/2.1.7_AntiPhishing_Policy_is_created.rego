# METADATA
# title: Ensure that an anti-phishing policy has been created
# description: |
#   By default, Office 365 includes built-in features that help protect users from phishing attacks. 
#   Set up anti-phishing polices to increase this protection, for example by refining settings 
#   to better detect and prevent impersonation and spoofing attacks. The default policy applies 
#   to all users within the organization and is a single view to fine-tune anti-phishing protection. 
#   Custom policies can be created and configured for specific users, groups or domains within the organization 
#   and will take precedence over the default policy for the scoped users.
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.7
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_7

default result := {"compliant": false, "message": "Evaluation failed"}

policies := object.get(input, "anti_phish_policies", object.get(input, "antiPhishPolicies", []))
rules := object.get(input, "anti_phish_rules", object.get(input, "antiPhishRules", []))

required_policy_fields := {
  "Enabled": true,
  "PhishThresholdLevel": 3,
  "EnableTargetedUserProtection": true,
  "EnableOrganizationDomainsProtection": true,
  "EnableMailboxIntelligence": true,
  "EnableMailboxIntelligenceProtection": true,
  "EnableSpoofIntelligence": true,
  "TargetedUserProtectionAction": "Quarantine",
  "TargetedDomainProtectionAction": "Quarantine",
  "MailboxIntelligenceProtectionAction": "Quarantine",
  "EnableFirstContactSafetyTips": true,
  "EnableSimilarUsersSafetyTips": true,
  "EnableSimilarDomainsSafetyTips": true,
  "EnableUnusualCharactersSafetyTips": true,
  "HonorDmarcPolicy": true
}

matching_policy[policy_obj] if {
  policy_obj := policies[_]

  # All required fields must match
  count({k | required_policy_fields[k] == policy_obj[k]}) == count(required_policy_fields)

  # Targeted users must be within limits
  count(policy_obj.TargetedUsersToProtect) > 0
  count(policy_obj.TargetedUsersToProtect) <= 350
}

matching_rule[rule_obj] if {
  rule_obj := rules[_]
  rule_obj.State == "Enabled"

  matching_policy[policy_obj]   # ✅ unique variable name
  rule_obj.AntiPhishPolicy == policy_obj.Name
}

targets_majority(rule_obj) if {
  count(rule_obj.RecipientDomainIs) > 0
  count(rule_obj.SentToMemberOf) > 0
}

# Compliant: matching policy + enabled rule + targets majority
antiphish_configured if {
  matching_rule[rule_obj]
  targets_majority(rule_obj)
}

# Non-compliant: policies exist but none match requirements
antiphish_configured if {
  count(policies) > 0
  count({p | matching_policy[p]}) == 0
}

antiphish_configured = null if {
  count(policies) == 0
  count(rules) == 0
}

generate_message(true) := "Anti-Phish policy and rules are correctly configured and enabled"
generate_message(false) := "Anti-Phish policy or rules are misconfigured or not enforced"
generate_message(null) := "Unable to determine Anti-Phish policy or rule configuration"

generate_affected_resources(true, _) := []

generate_affected_resources(false, data_input) := [
  pol.Name |
  pol := data_input[_]
]

generate_affected_resources(null, _) := ["Anti-Phish configuration status unknown"]

result := {
  "compliant": antiphish_configured == true,
  "message": generate_message(antiphish_configured),
  "affected_resources": generate_affected_resources(antiphish_configured, policies),
  "details": {
    "anti_phish_policies_evaluated": count(policies),
    "anti_phish_rules_evaluated": count(rules),
    "targeted_user_limit": 350,
    "required_policy_settings": required_policy_fields
  }
}
