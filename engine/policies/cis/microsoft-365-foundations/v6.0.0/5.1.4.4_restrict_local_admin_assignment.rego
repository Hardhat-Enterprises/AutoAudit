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


default compliant := false


# PASS when Selected users/groups are configured
compliant if {
	input.local_admin_registering_users_type ==
	"#microsoft.graph.enumeratedDeviceRegistrationMembership"
}


# PASS when nobody is automatically added as local admin
compliant if {
	input.local_admin_registering_users_type ==
	"#microsoft.graph.noDeviceRegistrationMembership"
}


msg := "Local administrator assignment during Entra join is limited" if {
	compliant
}


msg := "All users registering Entra joined devices are assigned local administrator rights" if {
	not compliant
}


result := output if {

	output := {
		"compliant": compliant,
		"message": msg,
		"details": {
			"local_admin_registering_users_type": input.local_admin_registering_users_type,
			"global_admins_enabled": input.enable_global_admins,
		},
	}
}