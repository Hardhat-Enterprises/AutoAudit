# METADATA
# title: Ensure Safe Attachments for SharePoint, OneDrive, and Microsoft Teams is Enabled
# description: |
#   Safe Attachments for SharePoint, OneDrive, and Microsoft Teams scans these services for malicious files.
#
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.5
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Defender
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_5

default result := {
    "compliant": false,
    "message": "Unable to determine Safe Attachments configuration for SharePoint, OneDrive, and Teams",
    "affected_resources": [],
    "details": {"policies_evaluated": []},
}

# The values CIS 2.1.5 requires for each setting.
required_settings := {
    "EnableATPForSPOTeamsODB": true,
    "EnableSafeDocs": true,
    "AllowSafeDocsOpen": false,
}

# Fail closed: the evidence only counts if atp_policy is an object
# and all three settings are present as true/false values.
evidence_present if {
    is_object(input.atp_policy)
    every setting, _ in required_settings {
        is_boolean(object.get(input.atp_policy, setting, null))
    }
}

# Settings that do not match what CIS requires.
wrong_settings contains setting if {
    some setting, required in required_settings
    input.atp_policy[setting] != required
}

# Any one wrong setting fails the control.
default compliant := false

compliant if {
    evidence_present
    count(wrong_settings) == 0
}

message_text := "Safe Attachments for SharePoint, OneDrive, and Teams is configured securely" if compliant

message_text := "Safe Attachments for SharePoint, OneDrive, or Teams is not configured securely" if not compliant

affected_list := [] if compliant

affected_list := [object.get(input.atp_policy, "Name", "Default")] if not compliant

result := {
    "compliant": compliant,
    "message": message_text,
    "affected_resources": affected_list,
    "details": {
        "policies_evaluated": [input.atp_policy],
        "non_compliant_settings": sort(wrong_settings),
    },
} if {
    evidence_present
}
