package cis.microsoft_365_foundations.v6_0_0.test_control_5_1_4_2

import rego.v1

test_compliant_at_maximum if {
  result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_2.result with input as {
    "user_device_quota": 20,
  }

  result.compliant == true
  result.details.user_device_quota == 20
  result.details.recommended_maximum == 20
}

test_compliant_below_maximum if {
  result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_2.result with input as {
    "user_device_quota": 10,
  }

  result.compliant == true
}

test_non_compliant_above_maximum if {
  result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_2.result with input as {
    "user_device_quota": 21,
  }

  result.compliant == false
  result.message == "Maximum devices per user exceeds the CIS recommended limit"
  result.details.user_device_quota == 21
  result.details.recommended_maximum == 20
}

test_non_compliant_null_quota if {
  result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_2.result with input as {
    "user_device_quota": null,
  }

  result.compliant == false
  result.message == "Unable to determine maximum devices per user"
}

test_non_compliant_missing_quota if {
  result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_2.result with input as {}

  result.compliant == false
  result.message == "Unable to determine maximum devices per user"
}
