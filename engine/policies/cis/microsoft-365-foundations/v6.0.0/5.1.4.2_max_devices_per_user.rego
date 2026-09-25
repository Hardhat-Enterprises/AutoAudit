# METADATA
# title: Ensure the maximum number of devices per user is limited
# description: Limit the maximum number of devices a user can register.
# related_resources:
# - ref: https://learn.microsoft.com/en-us/entra/identity/devices/device-management-azure-portal
#   description: Microsoft Entra device settings
# custom:
#   control_id: CIS-5.1.4.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: EntraID
#   requires_permissions:
#   - Policy.Read.DeviceConfiguration

package cis.microsoft_365_foundations.v6_0_0.control_5_1_4_2

import rego.v1

recommended_maximum := 20

default compliant := false

compliant if {
	input.user_device_quota != null
	is_number(input.user_device_quota)
	input.user_device_quota <= recommended_maximum
}

result := {
	"compliant": compliant,
	"message": message,
	"details": {
		"user_device_quota": object.get(input, "user_device_quota", null),
		"recommended_maximum": recommended_maximum,
	},
}

message := "Maximum devices per user is within the CIS recommended limit" if {
	compliant
}

message := "Maximum devices per user exceeds the CIS recommended limit" if {
	input.user_device_quota != null
	is_number(input.user_device_quota)
	input.user_device_quota > recommended_maximum
}

message := "Unable to determine maximum devices per user" if {
	object.get(input, "user_device_quota", null) == null
}

message := "Maximum devices per user value is invalid" if {
	input.user_device_quota != null
	not is_number(input.user_device_quota)
}
