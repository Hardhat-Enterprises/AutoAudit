package cis.microsoft_365_foundations.v6_0_0.test_control_2_4_2

import rego.v1

# --- Compliant ---

test_compliant_scoped_via_sent_to if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_2_4_2.result with input as {
		"atp_strict_rule_found": true,
		"atp_strict_rule_state": "Enabled",
		"atp_strict_rule_sent_to": ["ceo@contoso.com"],
		"atp_strict_rule_sent_to_member_of": [],
		"atp_strict_rule_recipient_domain_is": [],
		"eop_strict_rule_found": true,
		"eop_strict_rule_state": "Enabled",
		"eop_strict_rule_sent_to": ["ceo@contoso.com"],
		"eop_strict_rule_sent_to_member_of": [],
		"eop_strict_rule_recipient_domain_is": [],
	}
	result.compliant == true
	contains(result.message, "enabled and scoped")
}

test_compliant_scoped_via_sent_to_member_of if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_2_4_2.result with input as {
		"atp_strict_rule_found": true,
		"atp_strict_rule_state": "Enabled",
		"atp_strict_rule_sent_to": [],
		"atp_strict_rule_sent_to_member_of": ["Priority Accounts"],
		"atp_strict_rule_recipient_domain_is": [],
		"eop_strict_rule_found": true,
		"eop_strict_rule_state": "Enabled",
		"eop_strict_rule_sent_to": [],
		"eop_strict_rule_sent_to_member_of": ["Priority Accounts"],
		"eop_strict_rule_recipient_domain_is": [],
	}
	result.compliant == true
}

# --- Non-compliant: disabled ---

test_non_compliant_atp_disabled if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_2_4_2.result with input as {
		"atp_strict_rule_found": true,
		"atp_strict_rule_state": "Disabled",
		"atp_strict_rule_sent_to": ["ceo@contoso.com"],
		"atp_strict_rule_sent_to_member_of": [],
		"atp_strict_rule_recipient_domain_is": [],
		"eop_strict_rule_found": true,
		"eop_strict_rule_state": "Enabled",
		"eop_strict_rule_sent_to": ["ceo@contoso.com"],
		"eop_strict_rule_sent_to_member_of": [],
		"eop_strict_rule_recipient_domain_is": [],
	}
	result.compliant == false
	contains(result.message, "missing, disabled, or not scoped")
	result.details.atp_strict_rule_scoped == false
	result.details.eop_strict_rule_scoped == true
}

# --- Non-compliant: rule exists and is enabled but not scoped to anyone ---

test_non_compliant_not_scoped if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_2_4_2.result with input as {
		"atp_strict_rule_found": true,
		"atp_strict_rule_state": "Enabled",
		"atp_strict_rule_sent_to": [],
		"atp_strict_rule_sent_to_member_of": [],
		"atp_strict_rule_recipient_domain_is": [],
		"eop_strict_rule_found": true,
		"eop_strict_rule_state": "Enabled",
		"eop_strict_rule_sent_to": [],
		"eop_strict_rule_sent_to_member_of": [],
		"eop_strict_rule_recipient_domain_is": [],
	}
	result.compliant == false
}

# --- Non-compliant: EOP rule missing entirely ---

test_non_compliant_eop_rule_missing if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_2_4_2.result with input as {
		"atp_strict_rule_found": true,
		"atp_strict_rule_state": "Enabled",
		"atp_strict_rule_sent_to": ["ceo@contoso.com"],
		"atp_strict_rule_sent_to_member_of": [],
		"atp_strict_rule_recipient_domain_is": [],
		"eop_strict_rule_found": false,
		"eop_strict_rule_state": null,
		"eop_strict_rule_sent_to": [],
		"eop_strict_rule_sent_to_member_of": [],
		"eop_strict_rule_recipient_domain_is": [],
	}
	result.compliant == false
	result.details.eop_strict_rule_scoped == false
}

# --- Fail closed: no evidence at all ---

test_unable_to_determine_when_missing if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_2_4_2.result with input as {}
	result.compliant == false
	result.message == "Unable to determine Strict Preset Security Policy configuration"
}

test_unable_to_determine_when_found_flags_null if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_2_4_2.result with input as {
		"atp_strict_rule_found": null,
		"eop_strict_rule_found": null,
	}
	result.compliant == false
	result.message == "Unable to determine Strict Preset Security Policy configuration"
}