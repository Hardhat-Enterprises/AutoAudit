package cis.microsoft_365_foundations.v6_0_0.control_1_3_9

import rego.v1

default result := {
	"compliant": false,
	"message": "Unable to determine Bookings configuration",
	"details": {},
}

# Compliant via the default OWA policy disabling Bookings mailbox creation.
default owa_policy_disabled := false

owa_policy_disabled if input.default_policy_bookings_mailbox_creation_enabled == false

# Compliant via Bookings disabled tenant-wide (Get-OrganizationConfig) — a
# stronger, still-compliant state regardless of the OWA policy flag.
default tenant_bookings_disabled := false

tenant_bookings_disabled if object.get(input, "bookings_enabled", null) == false

# Either path satisfies CIS 1.3.9.
default compliant := false

compliant if owa_policy_disabled

compliant if tenant_bookings_disabled

result := output if {
	is_boolean(input.default_policy_bookings_mailbox_creation_enabled)

	output := {
		"compliant": compliant,
		"message": generate_message(compliant),
		"details": {
			"default_policy_bookings_mailbox_creation_enabled": input.default_policy_bookings_mailbox_creation_enabled,
			"bookings_enabled": object.get(input, "bookings_enabled", null),
			"policies_with_bookings": object.get(input, "policies_with_bookings", []),
			"total_policies": object.get(input, "total_policies", null),
		},
	}
}

generate_message(true) := "Shared Bookings is restricted: either the default OWA policy disables Bookings mailbox creation, or Bookings is disabled tenant-wide"

generate_message(false) := "Shared Bookings mailbox creation is enabled by the default OWA policy, and Bookings is not disabled tenant-wide; access is not restricted to select users"