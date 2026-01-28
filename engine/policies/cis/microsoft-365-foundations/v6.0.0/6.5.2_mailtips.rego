# METADATA
# title: Ensure MailTips are enabled for end users
# description: |
#   MailTips provide informational messages to users as they compose emails,
#   helping prevent accidental data disclosure and improving email hygiene.
#   Key settings include tips for external recipients and large audiences.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-6.5.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: low
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_6_5_2

default result := {"compliant": false, "message": "Evaluation failed"}

# Helper to check if all required settings are properly configured
all_settings_compliant(all_tips, external_tips, group_metrics, threshold) if {
    all_tips == true
    external_tips == true
    group_metrics == true
    threshold != null
    threshold > 0
}

result := output if {
    config := input.organization_config

    all_tips_enabled := config.MailTipsAllTipsEnabled
    external_tips_enabled := config.MailTipsExternalRecipientsTipsEnabled
    group_metrics_enabled := config.MailTipsGroupMetricsEnabled
    large_audience_threshold := config.MailTipsLargeAudienceThreshold

    # Compliant when all MailTips settings are properly configured
    compliant := all_settings_compliant(all_tips_enabled, external_tips_enabled, group_metrics_enabled, large_audience_threshold)

    output := {
        "compliant": compliant,
        "message": generate_message(all_tips_enabled, external_tips_enabled, group_metrics_enabled),
        "affected_resources": generate_affected_resources(all_tips_enabled, external_tips_enabled, group_metrics_enabled),
        "details": {
            "mail_tips_all_tips_enabled": all_tips_enabled,
            "mail_tips_external_recipients_enabled": external_tips_enabled,
            "mail_tips_group_metrics_enabled": group_metrics_enabled,
            "mail_tips_large_audience_threshold": large_audience_threshold
        }
    }
}

generate_message(all_tips, external_tips, group_metrics) := msg if {
    all_tips == true
    external_tips == true
    group_metrics == true
    msg := "MailTips are properly configured for end users"
}

generate_message(all_tips, external_tips, group_metrics) := msg if {
    not settings_all_true(all_tips, external_tips, group_metrics)
    msg := "MailTips are not fully configured for end users"
}

settings_all_true(all_tips, external_tips, group_metrics) if {
    all_tips == true
    external_tips == true
    group_metrics == true
}

generate_affected_resources(all_tips, external_tips, group_metrics) := resources if {
    all_tips == true
    external_tips == true
    group_metrics == true
    resources := []
}

generate_affected_resources(all_tips, external_tips, group_metrics) := resources if {
    not settings_all_true(all_tips, external_tips, group_metrics)
    resources := array.concat(
        array.concat(
            conditional_resource(all_tips != true, "MailTipsAllTipsEnabled is disabled"),
            conditional_resource(external_tips != true, "MailTipsExternalRecipientsTipsEnabled is disabled")
        ),
        conditional_resource(group_metrics != true, "MailTipsGroupMetricsEnabled is disabled")
    )
}

conditional_resource(true, msg) := [msg]
conditional_resource(false, _) := []
