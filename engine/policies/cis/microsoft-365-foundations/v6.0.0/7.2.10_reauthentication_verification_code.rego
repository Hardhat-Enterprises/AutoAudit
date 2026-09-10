# METADATA
# title: Ensure reauthentication with verification code is restricted
# description: Ensure verification-code users are required to reauthenticate within 15 days.
# custom:
#   control_id: CIS-7.2.10
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: SharePoint
#   requires_permissions:
#     - SharePoint.Admin

package cis.microsoft_365_foundations.v6_0_0.control_7_2_10

import rego.v1

default result := {
    "compliant": false,
    "message": "Unable to determine verification code reauthentication configuration",
    "details": {},
}

compliant if {
    input.email_attestation_required == true
    input.email_attestation_reauth_days <= 15
}

result := output if {
    is_boolean(object.get(input, "email_attestation_required", null))

    output := {
        "compliant": compliant,
        "message": generate_message(compliant),
        "details": {
            "email_attestation_required": input.email_attestation_required,
            "email_attestation_reauth_days": object.get(
                input,
                "email_attestation_reauth_days",
                null,
            ),
        },
    }
}

generate_message(true) := "Verification code reauthentication is restricted to 15 days or less"

generate_message(false) := "Verification code reauthentication is not restricted to 15 days or less"