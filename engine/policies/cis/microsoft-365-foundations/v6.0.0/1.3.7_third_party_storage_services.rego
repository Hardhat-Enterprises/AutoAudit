# METADATA
# title: Ensure 'third-party storage services' are restricted in 'Microsoft 365 on the web'
# description: |
#   Third-party storage services (Dropbox, Google Drive, Box, etc.) can be
#   enabled for users in Microsoft 365 on the web, allowing them to store and
#   share documents outside organizational control alongside OneDrive and
#   team sites. This increases the risk of data breaches and makes it
#   difficult to maintain data privacy and security. Restrict the "Third
#   Party Storage Services" service principal in Entra ID to prevent this.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.3.7
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Application.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_1_3_7

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    exists := input.service_principal_exists
    enabled := input.account_enabled
    is_compliant := is_restricted(exists, enabled)

    output := {
        "compliant": is_compliant,
        "message": generate_message(exists, enabled),
        "affected_resources": affected_resources(exists, enabled),
        "details": {
            "service_principal_exists": exists,
            "account_enabled": enabled,
            "app_id": "c1f33bc0-bdb4-4248-ba9b-096807ddb43e"
        }
    }
}

# Compliant only when the service principal has been created AND disabled
is_restricted(exists, enabled) := true if {
    exists == true
    enabled == false
} else := false

generate_message(exists, enabled) := msg if {
    exists == true
    enabled == false
    msg := "The 'Third Party Storage Services' service principal is disabled; third-party storage is restricted."
}

generate_message(exists, _) := msg if {
    exists == false
    msg := "The 'Third Party Storage Services' service principal has not been created; third-party storage remains available by default."
}

generate_message(exists, enabled) := msg if {
    exists == true
    enabled == true
    msg := "The 'Third Party Storage Services' service principal exists but is still enabled (accountEnabled: true)."
}

affected_resources(exists, enabled) := [] if {
    exists == true
    enabled == false
} else := ["Third Party Storage Services (appId: c1f33bc0-bdb4-4248-ba9b-096807ddb43e)"]