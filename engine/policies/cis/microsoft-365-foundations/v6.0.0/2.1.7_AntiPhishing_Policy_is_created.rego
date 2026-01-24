# METADATA
# title: Ensure that an anti-phishing policy has been created
# description: |
#   By default, Office 365 includes built-in features that help protect users from phishing attacks. 
#   Set up anti-phishing policies to increase this protection, for example by refining settings 
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

required_values := {
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

policy_compliant(p) if {
    invalid_fields := {f | required_values[f] != p[f]}
    count(invalid_fields) == 0
}

non_compliant_policies := [
    {"policy": p.Name, "failed_fields": [f | required_values[f] != p[f]]} |
    p := input.anti_phish_policies[_]
    not policy_compliant(p)
]

targeted_users := [user |
    p := input.anti_phish_policies[_]
    policy_compliant(p)
    user := p.TargetedUsersToProtect[_]
]

global_compliant_policies := [p |
    p := input.anti_phish_policies[_]
    policy_compliant(p)
    count(p.TargetedUsersToProtect) == 0
]

result := {
    "compliant": true,
    "message": sprintf(
        "Found %d user(s) protected by compliant anti-phishing policy (including global/default)",
        [count(targeted_users) + count(global_compliant_policies)]
    )
} if {
    count(targeted_users) + count(global_compliant_policies) > 0
}

result := {
    "compliant": false,
    "message": sprintf(
        "Non-compliant policies detected: %v",
        [non_compliant_policies]
    )
} if {
    count(non_compliant_policies) > 0
}
