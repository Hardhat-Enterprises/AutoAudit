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

bcc_suspicious_outbound_mail := object.get(
    input,
    "bcc_suspicious_outbound_mail",
    object.get(object.get(input, "default_policy", {}), "BccSuspiciousOutboundMail", null)
)

notify_outbound_spam := object.get(
    input,
    "notify_outbound_spam",
    object.get(object.get(input, "default_policy", {}), "NotifyOutboundSpam", null)
)

bcc_additional_recipients := object.get(
    object.get(input, "default_policy", {}),
    "BccSuspiciousOutboundAdditionalRecipients",
    null
)

notify_outbound_spam_recipients := object.get(
    object.get(input, "default_policy", {}),
    "NotifyOutboundSpamRecipients",
    null
)

bcc_recipients_count := count(bcc_additional_recipients) if {
    bcc_additional_recipients != null
} else := 0

notify_recipients_count := count(notify_outbound_spam_recipients) if {
    notify_outbound_spam_recipients != null
} else := 0

outbound_spam_monitoring_enabled := true if {
    bcc_suspicious_outbound_mail == true
    notify_outbound_spam == true
    bcc_additional_recipients != null
    notify_outbound_spam_recipients != null
    bcc_recipients_count > 0
    notify_recipients_count > 0
}

outbound_spam_monitoring_enabled := false if {
    bcc_suspicious_outbound_mail != true
} else := false if {
    notify_outbound_spam != true
} else := false if {
    bcc_additional_recipients != null
    bcc_recipients_count == 0
} else := false if {
    notify_outbound_spam_recipients != null
    notify_recipients_count == 0
}

outbound_spam_monitoring_enabled := null if {
    bcc_suspicious_outbound_mail == null
    notify_outbound_spam == null
    bcc_additional_recipients == null
    notify_outbound_spam_recipients == null
}

result := output if {
    compliant := outbound_spam_monitoring_enabled == true

    output := {
        "compliant": compliant,
        "message": generate_message(outbound_spam_monitoring_enabled),
        "affected_resources": generate_affected_resources(outbound_spam_monitoring_enabled),
        "details": {
            "bcc_suspicious_outbound_mail": bcc_suspicious_outbound_mail,
            "bcc_additional_recipients": bcc_additional_recipients,
            "notify_outbound_spam": notify_outbound_spam,
            "notify_outbound_spam_recipients": notify_outbound_spam_recipients
        }
    }
}

generate_message(true) := "Outbound spam Bcc and notification settings are enabled and recipients are configured"
generate_message(false) := "Outbound spam Bcc or notification settings are disabled or missing recipients"
generate_message(null) := "Unable to determine outbound spam Bcc or notification configuration"

generate_affected_resources(true) := []
generate_affected_resources(false) := ["HostedOutboundSpamFilterPolicy"]
generate_affected_resources(null) := ["HostedOutboundSpamFilterPolicy status unknown"]
