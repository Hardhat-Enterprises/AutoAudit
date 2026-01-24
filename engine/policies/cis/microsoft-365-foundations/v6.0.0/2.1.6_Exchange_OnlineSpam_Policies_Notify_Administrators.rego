# METADATA
# title: Ensure Exchange Online Spam Policies are set to notify administrators
# description: |
#   In Microsoft 365 organizations with mailboxes in Exchange Online or 
#   standalone Exchange Online Protection organizations without Exchange
#   Online mailboxes, email messages are automatically protected against spam by EOP.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations benchmark
# custom:
#   control_id: CIS-2.1.6
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_6

missing_bcc if {
    not input.default_policy.bcc_suspicious_outbound_mail
}

missing_notify if {
    not input.default_policy.notify_outbound_spam
}

missing_settings := array.concat(
    [s | s := "bcc_suspicious_outbound_mail"; missing_bcc],
    [s | s := "notify_outbound_spam"; missing_notify]
)

outbound_spam_monitoring_enabled if {
    count(missing_settings) == 0
}

scan_result = {
    "compliant": true,
    "message": "Outbound spam BCC and notification settings are enabled",
    "affected_resources": [],
    "details": {
        "bcc_suspicious_outbound_mail": input.default_policy.bcc_suspicious_outbound_mail,
        "notify_outbound_spam": input.default_policy.notify_outbound_spam,
        "auto_forwarding_mode": input.default_policy.auto_forwarding_mode
    }
} if {
    outbound_spam_monitoring_enabled
}

scan_result = {
    "compliant": false,
    "message": generate_message_missing,
    "affected_resources": ["HostedOutboundSpamFilterPolicy"],
    "details": {
        "bcc_suspicious_outbound_mail": input.default_policy.bcc_suspicious_outbound_mail,
        "notify_outbound_spam": input.default_policy.notify_outbound_spam,
        "auto_forwarding_mode": input.default_policy.auto_forwarding_mode
    }
} if {
    not outbound_spam_monitoring_enabled
}

generate_message_missing := msg if {
    count(missing_settings) > 0
    msg := sprintf(
        "Outbound spam settings disabled or misconfigured: %v",
        [missing_settings]
    )
}

generate_message_missing := "Unable to determine outbound spam BCC or notification configuration" if {
    count(missing_settings) == 0
}
