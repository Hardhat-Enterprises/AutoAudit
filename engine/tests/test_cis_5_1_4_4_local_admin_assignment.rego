package cis.microsoft_365_foundations.v6_0_0.test_control_5_1_4_4

import rego.v1

test_compliant_enumerated_membership if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4.result with input as {
		"local_admin_registering_users_type": "#microsoft.graph.enumeratedDeviceRegistrationMembership",
		"enable_global_admins": true,
	}
	result.compliant == true
	contains(result.message, "is limited")
}

test_compliant_no_membership if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4.result with input as {
		"local_admin_registering_users_type": "#microsoft.graph.noDeviceRegistrationMembership",
		"enable_global_admins": false,
	}
	result.compliant == true
	contains(result.message, "is limited")
}

test_non_compliant_all_users if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4.result with input as {
		"local_admin_registering_users_type": "#microsoft.graph.allDeviceRegistrationMembership",
		"enable_global_admins": true,
	}
	result.compliant == false
	contains(result.message, "All users registering Entra joined devices are assigned local administrator rights")
}

test_unable_to_determine_when_null if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4.result with input as {
		"local_admin_registering_users_type": null,
		"enable_global_admins": null,
	}
	result.compliant == false
	result.message == "Unable to determine Entra join local administrator assignment configuration"
}

test_unable_to_determine_when_missing if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4.result with input as {}
	result.compliant == false
	result.message == "Unable to determine Entra join local administrator assignment configuration"
}

test_unable_to_determine_when_unrecognised_type if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_5_1_4_4.result with input as {
		"local_admin_registering_users_type": "#microsoft.graph.someFutureNewType",
	}
	result.compliant == false
	result.message == "Unable to determine Entra join local administrator assignment configuration"
}