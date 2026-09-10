package cis.microsoft_365_foundations.v6_0_0.control_7_2_10

import rego.v1

test_compliant_at_15_days if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_10.result with input as {
        "email_attestation_required": true,
        "email_attestation_reauth_days": 15,
    }

    result.compliant == true
}

test_compliant_under_15_days if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_10.result with input as {
        "email_attestation_required": true,
        "email_attestation_reauth_days": 10,
    }

    result.compliant == true
}

test_non_compliant_over_15_days if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_10.result with input as {
        "email_attestation_required": true,
        "email_attestation_reauth_days": 16,
    }

    result.compliant == false
}

test_non_compliant_when_reauthentication_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_10.result with input as {
        "email_attestation_required": false,
        "email_attestation_reauth_days": 15,
    }

    result.compliant == false
}

test_missing_configuration_fails_closed if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_10.result with input as {}

    result.compliant == false
}