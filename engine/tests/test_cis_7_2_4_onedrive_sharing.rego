package cis.microsoft_365_foundations.v6_0_0.control_7_2_4

import rego.v1

# ---- Compliant cases ----

test_compliant_disabled if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_4.result with input as {
        "sharing_capability": 0
    }
    result.compliant == true
}

test_compliant_external_user_sharing_only if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_4.result with input as {
        "sharing_capability": 1
    }
    result.compliant == true
}

test_compliant_existing_external_user_sharing_only if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_4.result with input as {
        "sharing_capability": 3
    }
    result.compliant == true
}

# ---- Non-compliant case ----

test_non_compliant_external_user_and_guest_sharing if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_4.result with input as {
        "sharing_capability": 2
    }
    result.compliant == false
    result.details.sharing_capability == 2
}

# ---- Missing / empty data cases ----

test_missing_sharing_capability_key if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_4.result with input as {}
    result.compliant == false
}

test_null_sharing_capability if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_4.result with input as {
        "sharing_capability": null
    }
    result.compliant == false
}

# ---- Result structure sanity check ----

test_result_structure if {
    result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_4.result with input as {
        "sharing_capability": 2
    }
    result.compliant == false
    result.message != ""
    result.details.sharing_capability == 2
}