# METADATA
# title: Ensure local administrator assignment is limited during Entra join
# description: Ensure users registering Microsoft Entra joined devices are not automatically granted local administrator privileges.
# custom:
#   control_id: CIS-5.1.4.4
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.DeviceConfiguration

package cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4

import rego.v1

default result := {
	"compliant": false,
	"message": "Unable to determine Entra join local administrator assignment configuration",
	"details": {},
}

known_membership_types := {
	"#microsoft.graph.enumeratedDeviceRegistrationMembership",
	"#microsoft.graph.noDeviceRegistrationMembership",
	"#microsoft.graph.allDeviceRegistrationMembership",
}

result := output if {
	membership_type := input.local_admin_registering_users_type
	membership_type in known_membership_types

	compliant := membership_type != "#microsoft.graph.allDeviceRegistrationMembership"

	output := {
		"compliant": compliant,
		"message": generate_message(compliant),
		"details": {
			"local_admin_registering_users_type": membership_type,
			"global_admins_enabled": object.get(input, "enable_global_admins", null),
		},
	}
}

generate_message(true) := "Local administrator assignment during Entra join is limited"

generate_message(false) := "All users registering Entra joined devices are assigned local administrator rights"