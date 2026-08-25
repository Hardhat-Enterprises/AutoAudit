package cis.microsoft_365_foundations.v6_0_0.control_1_3_9

import rego.v1

default result := {
  "compliant": false,
  "message": "Unable to determine Bookings configuration",
  "details": {}
}

result := output if {
  is_boolean(input.default_policy_bookings_mailbox_creation_enabled)

  compliant := input.default_policy_bookings_mailbox_creation_enabled == false

  output := {
    "compliant": compliant,
    "message": generate_message(compliant),
    "details": {
      "default_policy_bookings_mailbox_creation_enabled": input.default_policy_bookings_mailbox_creation_enabled,
      "policies_with_bookings": object.get(input, "policies_with_bookings", []),
      "total_policies": object.get(input, "total_policies", null),
    }
  }
}

generate_message(true) := "Shared Bookings mailbox creation is disabled by default; access is restricted to select users"
generate_message(false) := "Shared Bookings mailbox creation is enabled by the default OWA policy; access is not restricted to select users"