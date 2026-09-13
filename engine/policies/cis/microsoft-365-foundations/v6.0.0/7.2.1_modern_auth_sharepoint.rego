# METADATA
# title: Ensure modern authentication for SharePoint applications is required
# description: |
#   Modern authentication in Microsoft 365 enables stronger authentication
#   mechanisms (MFA, certificate-based authentication, third-party SAML
#   identity providers) when establishing sessions between applications,
#   SharePoint, and connecting users. If legacy authentication protocols
#   remain enabled, strong authentication controls such as MFA can be
#   bypassed, allowing apps and users to authenticate to SharePoint using
#   weaker, non-modern methods.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: SharePoint
#   requires_permissions:
#   - SharePoint.Admin

package cis.microsoft_365_foundations.v6_0_0.control_7_2_1

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
    legacy_auth := input.legacy_auth_protocols_enabled
    is_compliant := is_restricted(legacy_auth)

    output := {
        "compliant": is_compliant,
        "message": generate_message(legacy_auth),
        "affected_resources": affected_resources(legacy_auth),
        "details": {
            "legacy_auth_protocols_enabled": legacy_auth
        }
    }
}

# Compliant only when legacy auth protocols are explicitly disabled.
# Missing/null evidence must not silently pass.
is_restricted(legacy_auth) := true if {
    legacy_auth == false
} else := false

generate_message(legacy_auth) := msg if {
    legacy_auth == false
    msg := "Legacy authentication protocols are disabled for SharePoint; modern authentication is required."
}

generate_message(legacy_auth) := msg if {
    legacy_auth == true
    msg := "Legacy authentication protocols are enabled for SharePoint; modern authentication is not enforced."
}

generate_message(legacy_auth) := msg if {
    legacy_auth == null
    msg := "SharePoint tenant evidence for legacy authentication protocols is missing; unable to confirm modern authentication is enforced."
}

affected_resources(legacy_auth) := [] if {
    legacy_auth == false
} else := ["SharePoint tenant (LegacyAuthProtocolsEnabled)"]