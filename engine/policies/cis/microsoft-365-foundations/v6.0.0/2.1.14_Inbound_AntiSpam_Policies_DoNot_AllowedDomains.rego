# METADATA
# title: Ensure inbound anti-spam policies do not contain allowed domains
# description: |
#   Anti-spam protection is a feature of Exchange Online that utilizes policies
#   to help to reduce the amount of junk email bulk and phishing emails a mailbox receives.
#   These policies contain lists to allow or block specific senders or domains.
#    • The allowed senders list
#    • The allowed domains list
#    • The blocked senders list
#    • The blocked domains list
#   The recommended state is: Do not define any Allowed domains
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.14
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_14

default result := {"compliant": false, "message": "Evaluation failed"}

allowed_sender_domains_undefined := true if {
    input.AllowedSenderDomains == null
}

allowed_sender_domains_undefined := true if {
    input.AllowedSenderDomains != null
    count(input.AllowedSenderDomains) == 0
}

allowed_sender_domains_undefined := false if {
    input.AllowedSenderDomains != null
    count(input.AllowedSenderDomains) > 0
}

result := output if {
    compliant := allowed_sender_domains_undefined == true

    output := {
        "compliant": compliant,
        "message": generate_message(allowed_sender_domains_undefined),
        "affected_resources": generate_affected_resources(allowed_sender_domains_undefined),
        "details": {
            "AllowedSenderDomains": input.AllowedSenderDomains
        }
    }
}

generate_message(true) := "AllowedSenderDomains is undefined or empty for the policy"
generate_message(false) := "AllowedSenderDomains is defined for the policy"

generate_affected_resources(true) := []
generate_affected_resources(false) := ["HostedContentFilterPolicy"]
