# METADATA
# title: Ensure SMTP AUTH is disabled
# description: |
#   SMTP AUTH allows clients to submit email using basic authentication,
#   which is vulnerable to credential theft attacks. Disable SMTP AUTH
#   at the organization level to enforce modern authentication methods.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-6.5.4
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_6_5_4

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    smtp_auth_disabled := input.smtp_client_authentication_disabled

    # Compliant when SMTP client authentication is disabled
    compliant := smtp_auth_disabled == true

    output := {
        "compliant": compliant,
        "message": generate_message(smtp_auth_disabled),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "smtp_client_authentication_disabled": smtp_auth_disabled
        }
    }
}

generate_message(smtp_auth_disabled) := msg if {
    smtp_auth_disabled == true
    msg := "SMTP AUTH is disabled at the organization level"
}

generate_message(smtp_auth_disabled) := msg if {
    smtp_auth_disabled == false
    msg := "SMTP AUTH is enabled at the organization level"
}

generate_message(smtp_auth_disabled) := msg if {
    smtp_auth_disabled == null
    msg := "Unable to determine SMTP AUTH status"
}

generate_affected_resources(true) := []
generate_affected_resources(false) := ["SMTP AUTH is enabled"]
