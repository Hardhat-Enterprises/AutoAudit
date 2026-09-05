package cis.microsoft_365_foundations.v6_0_0.test_control_1_3_6

import rego.v1

test_compliant_customer_lockbox_enabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_6.result with input as {
        "customer_lockbox_enabled": true
    }
    result.compliant == true
}

test_non_compliant_customer_lockbox_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_6.result with input as {
        "customer_lockbox_enabled": false
    }
    result.compliant == false
}

test_unknown_status_null if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_6.result with input as {
        "customer_lockbox_enabled": null
    }
    result.compliant == false
}

test_missing_field if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_1_3_6.result with input as {}
    result.compliant == false
}