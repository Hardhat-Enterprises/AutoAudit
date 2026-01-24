# METADATA
# title: Ensure modern authentication for Exchange Online is enabled
# description: |
#   Modern authentication (OAuth 2.0) provides enhanced security features
#   including MFA support and conditional access. OAuth2ClientProfileEnabled
#   must be set to True for Exchange Online.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-6.5.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_6_5_1

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    oauth_enabled := input.oauth_enabled

    # Compliant when OAuth authentication is enabled
    compliant := oauth_enabled == true

    output := {
        "compliant": compliant,
        "message": generate_message(oauth_enabled),
        "affected_resources": generate_affected_resources(compliant),
        "details": {
            "oauth2_client_profile_enabled": oauth_enabled
        }
    }
}

generate_message(oauth_enabled) := msg if {
    oauth_enabled == true
    msg := "Modern authentication (OAuth 2.0) is enabled for Exchange Online"
}

generate_message(oauth_enabled) := msg if {
    oauth_enabled == false
    msg := "Modern authentication (OAuth 2.0) is disabled for Exchange Online"
}

generate_message(oauth_enabled) := msg if {
    oauth_enabled == null
    msg := "Unable to determine modern authentication status"
}

generate_affected_resources(true) := []
generate_affected_resources(false) := ["Modern authentication is disabled"]
