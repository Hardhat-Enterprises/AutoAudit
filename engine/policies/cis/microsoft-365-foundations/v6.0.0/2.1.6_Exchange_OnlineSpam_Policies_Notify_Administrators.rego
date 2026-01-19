# METADATA
# title: Ensure Exchange Online Spam Policies are set to notify administrators
# description: |
#   In Microsoft 365 organizations with mailboxes in Exchange Online or 
#   standalone Exchange Online Protection organizations without Exchange
#   Online mailboxes, email messages are automatically protected against spam (junk email) by EOP.
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.6
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_6

default result := {"compliant": false, "message": "Evaluation failed"}

outbound_spam_monitoring_enabled := true if {
    input.BccSuspiciousOutboundMail == true
    input.NotifyOutboundSpam == true
    count(input.BccSuspiciousOutboundAdditionalRecipients) > 0
    count(input.NotifyOutboundSpamRecipients) > 0
}

outbound_spam_monitoring_enabled := false if {
    input.BccSuspiciousOutboundMail != true
} else := false if {
    input.NotifyOutboundSpam != true
} else := false if {
    count(input.BccSuspiciousOutboundAdditionalRecipients) == 0
} else := false if {
    count(input.NotifyOutboundSpamRecipients) == 0
}

outbound_spam_monitoring_enabled := null if {
    not input.BccSuspiciousOutboundMail
    not input.NotifyOutboundSpam
    not input.BccSuspiciousOutboundAdditionalRecipients
    not input.NotifyOutboundSpamRecipients
}

result := output if {
    compliant := outbound_spam_monitoring_enabled == true

    output := {
        "compliant": compliant,
        "message": generate_message(outbound_spam_monitoring_enabled),
        "affected_resources": generate_affected_resources(outbound_spam_monitoring_enabled),
        "details": {
            "bcc_suspicious_outbound_mail": input.BccSuspiciousOutboundMail,
            "bcc_additional_recipients": input.BccSuspiciousOutboundAdditionalRecipients,
            "notify_outbound_spam": input.NotifyOutboundSpam,
            "notify_outbound_spam_recipients": input.NotifyOutboundSpamRecipients
        }
    }
}

generate_message(true) := "Outbound spam Bcc and notification settings are enabled and recipients are configured"
generate_message(false) := "Outbound spam Bcc or notification settings are disabled or missing recipients"
generate_message(null) := "Unable to determine outbound spam Bcc or notification configuration"

generate_affected_resources(true) := []
generate_affected_resources(false) := ["HostedOutboundSpamFilterPolicy"]
generate_affected_resources(null) := ["HostedOutboundSpamFilterPolicy status unknown"]
