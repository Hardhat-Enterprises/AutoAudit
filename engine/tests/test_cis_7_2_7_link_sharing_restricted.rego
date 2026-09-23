package cis.microsoft_365_foundations.v6_0_0.test_control_7_2_7

import rego.v1

# --- Compliant ---

test_compliant_direct_specific_people if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_7.result with input as {"default_sharing_link_type": 1}
	result.compliant == true
	contains(result.message, "'Direct'")
	result.details.default_sharing_link_type_name == "Direct"
}

test_compliant_internal_organization_only if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_7.result with input as {"default_sharing_link_type": 2}
	result.compliant == true
	contains(result.message, "'Internal'")
	result.details.default_sharing_link_type_name == "Internal"
}

# --- Non-compliant ---

test_non_compliant_anonymous_access if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_7.result with input as {"default_sharing_link_type": 3}
	result.compliant == false
	contains(result.message, "'AnonymousAccess'")
	result.details.default_sharing_link_type == 3
}

test_non_compliant_none_not_configured if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_7.result with input as {"default_sharing_link_type": 0}
	result.compliant == false
	contains(result.message, "'None'")
}

# --- Fail closed: unrecognised / out-of-range enum value ---

test_unable_to_determine_when_unrecognised_value if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_7.result with input as {"default_sharing_link_type": 99}
	result.compliant == false
	result.message == "Unable to determine the default sharing link type for SharePoint and OneDrive"
}

# --- Fail closed: no evidence at all ---

test_unable_to_determine_when_missing if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_7.result with input as {}
	result.compliant == false
	result.message == "Unable to determine the default sharing link type for SharePoint and OneDrive"
}

test_unable_to_determine_when_null if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_7.result with input as {"default_sharing_link_type": null}
	result.compliant == false
	result.message == "Unable to determine the default sharing link type for SharePoint and OneDrive"
}

test_unable_to_determine_when_string_instead_of_number if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_7_2_7.result with input as {"default_sharing_link_type": "Internal"}
	result.compliant == false
	result.message == "Unable to determine the default sharing link type for SharePoint and OneDrive"
}
