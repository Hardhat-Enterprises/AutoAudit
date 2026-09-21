package cis.microsoft_365_foundations.v6_0_0.control_1_3_2

import rego.v1

# Compliant: timeout is exactly 180 minutes (3 hours)
test_compliant_at_180_minutes if {
  r := evaluate_with({"idle_timeout_minutes": 180})
  r.compliant == true
}

# Compliant: timeout is less than 180 minutes
test_compliant_at_60_minutes if {
  r := evaluate_with({"idle_timeout_minutes": 60})
  r.compliant == true
}

# Non-compliant: timeout exceeds 180 minutes
test_non_compliant_at_240_minutes if {
  r := evaluate_with({"idle_timeout_minutes": 240})
  r.compliant == false
}

# Non-compliant: timeout is null (missing evidence)
test_non_compliant_when_null if {
  r := evaluate_with({"idle_timeout_minutes": null})
  r.compliant == false
}

# Non-compliant: timeout is zero (not configured)
test_non_compliant_when_zero if {
  r := evaluate_with({"idle_timeout_minutes": 0})
  r.compliant == false
}

# Non-compliant: collector failed to retrieve data
test_non_compliant_on_collector_error if {
  r := evaluate_with({
    "idle_timeout_minutes": null,
    "collector_error": "403 Forbidden",
  })
  r.compliant == false
}

# Helper: evaluate the policy with a given input
evaluate_with(input_data) := r if {
  r := result with input as input_data
}