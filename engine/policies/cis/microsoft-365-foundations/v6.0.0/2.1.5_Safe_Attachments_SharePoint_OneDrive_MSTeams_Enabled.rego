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
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_5

default result := {"compliant": false, "message": "Evaluation failed"}

policy := input.atp_policy

non_compliant_policies = [
    { "Name": "ATPPolicy", "Issue": "EnableATPForSPOTeamsODB is disabled" } 
    | policy.EnableATPForSPOTeamsODB == false
] + [
    { "Name": "ATPPolicy", "Issue": "EnableSafeDocs is disabled" } 
    | policy.EnableSafeDocs == false
] + [
    { "Name": "ATPPolicy", "Issue": "AllowSafeDocsOpen should be false" } 
    | policy.AllowSafeDocsOpen == true
]

compliant := count(non_compliant_policies) == 0

message_text := "Safe Attachments for SharePoint, OneDrive, and Teams is configured securely" {
    compliant
}

message_text := "Safe Attachments for SharePoint, OneDrive, or Teams is not configured securely" {
    not compliant
}

affected_list := [] {
    compliant
}

affected_list := non_compliant_policies {
    not compliant
}

result := {
    "compliant": compliant,
    "message": message_text,
    "affected_resources": affected_list,
    "details": {
        "policy_evaluated": policy
    }
}
