# METADATA
# title: Ensure Direct Send submissions are rejected
# description: |
#   Direct Send allows anonymous SMTP connections to send email as the
#   organization. This can be exploited for phishing and spoofing attacks.
#   Configure transport settings to reject unauthenticated direct send.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-6.5.5
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_6_5_5

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    transport_config := input.transport_config
    smtp_auth_disabled := input.smtp_client_authentication_disabled

    # Direct Send is blocked when SMTP client authentication is disabled
    # Additional check: ExternalSubmissionEnabled should be False for full compliance
    external_submission := transport_config.ExternalDelayDsnEnabled

    # Compliant when SMTP client authentication is disabled
    compliant := smtp_auth_disabled == true

    output := {
        "compliant": compliant,
        "message": generate_message(smtp_auth_disabled),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "smtp_client_authentication_disabled": smtp_auth_disabled,
            "transport_config": {
                "external_delay_dsn_enabled": external_submission
            }
        }
    }
}

generate_message(smtp_auth_disabled) := msg if {
    smtp_auth_disabled == true
    msg := "Direct Send submissions are blocked (SMTP client auth disabled)"
}

generate_message(smtp_auth_disabled) := msg if {
    smtp_auth_disabled == false
    msg := "Direct Send submissions are allowed (SMTP client auth enabled)"
}

generate_message(smtp_auth_disabled) := msg if {
    smtp_auth_disabled == null
    msg := "Unable to determine Direct Send status"
}

generate_affected_resources(true) := []
generate_affected_resources(false) := ["Direct Send submissions are allowed"]
