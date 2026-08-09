package cis.microsoft_365_foundations.v6_0_0.control_1_3_7_test

import rego.v1
import data.cis.microsoft_365_foundations.v6_0_0.control_1_3_7

test_compliant_no_external_storage if {
    result := control_1_3_7.result with input as {
        "total_policies": 1,
        "policies_with_external_storage": []
    }
    result.compliant == true
}

test_non_compliant_one_policy_allows_storage if {
    result := control_1_3_7.result with input as {
        "total_policies": 1,
        "policies_with_external_storage": ["Default"]
    }
    result.compliant == false
}

test_non_compliant_no_policies if {
    result := control_1_3_7.result with input as {
        "total_policies": 0,
        "policies_with_external_storage": []
    }
    result.compliant == false
}

test_result_structure if {
    result := control_1_3_7.result with input as {
        "total_policies": 1,
        "policies_with_external_storage": []
    }
    result.details.total_policies == 1
}