package cis.microsoft_365_foundations.v6_0_0.test_control_5_1_2_3

import rego.v1

test_compliant_when_non_admin_users_are_restricted if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_2_3.result with input as {
        "allowed_to_create_tenants": false
    }

    result.compliant == true
    result.details.allowed_to_create_tenants == false
}

test_non_compliant_when_non_admin_users_can_create_tenants if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_2_3.result with input as {
        "allowed_to_create_tenants": true
    }

    result.compliant == false
    result.details.allowed_to_create_tenants == true
}

test_non_compliant_when_setting_is_missing if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_2_3.result with input as {}

    result.compliant == false
    result.message == "Unable to determine allowedToCreateTenants"
}
