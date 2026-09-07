package cis.microsoft_365_foundations.v6_0_0.test_control_2_4_2

import rego.v1

# --- Compliant: both rules enabled, scoped, and matching via SentTo ---

test_compliant_matching_sent_to if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_2_4_2.result with input as {
		"atp_strict_rule_found": true,
		"atp_strict_rule_state": "Enabled",
		"atp_strict_rule_sent_to": ["ceo@contoso.com", "cfo@contoso.com"],
		"atp_strict_rule_sent_to_member_of": [],
		"atp_strict_rule_recipient_domain_is": [],
		"eop_strict_rule_found": true,
		"eop_strict_rule_state": "Enabled",
		"eop_strict_rule_sent_to": ["cfo@contoso.com", "ceo@contoso.com"],
		"eop_strict_rule_sent_to_member_of": [],
		"eop_strict_rule_recipient_domain_is": [],
	}
	result.compliant == true
	contains(result.message, "same priority accounts")
}

# --- Compliant: both rules matching via SentToMemberOf (group-based scoping) ---

test_compliant_matching_sent_to_member_of if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_2_4_2.result with input as {
		"atp_strict_rule_found": true,
		"atp_strict_rule_state": "Enabled",
		"atp_strict_rule_sent_to": [],
		"atp_strict_rule_sent_to_member_of": ["Executives"],
		"atp_strict_rule_recipient_domain_is": [],
		"eop_strict_rule_found": true,
		"eop_strict_rule_state": "Enabled",
		"eop_strict_rule_sent_to": [],
		"eop_strict_rule_sent_to_member_of": ["Executives"],
		"eop_strict_rule_recipient_domain_is": [],
	}
	result.compliant == true
}

# --- Non-compliant: the Codex-flagged case — different recipients on each side ---

test_non_compliant_mismatched_recipients if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_2_4_2.result with input as {
		"atp_strict_rule_found": true,
		"atp_strict_rule_state": "Enabled",
		"atp_strict_rule_sent_to": ["ceo@contoso.com"],
		"atp_strict_rule_sent_to_member_of": [],
		"atp_strict_rule_recipient_domain_is": [],
		"eop_strict_rule_found": true,
		"eop_strict_rule_state": "Enabled",
		"eop_strict_rule_sent_to": ["cfo@contoso.com"],
		"eop_strict_rule_sent_to_member_of": [],
		"eop_strict_rule_recipient_domain_is": [],
	}
	result.compliant == false
	result.details.atp_strict_rule_scoped == true
	result.details.eop_strict_rule_scoped == true
	result.details.same_priority_accounts_covered == false
}

# --- Non-compliant: partial overlap is still not good enough (not the SAME set) ---

test_non_compliant_partial_overlap if {
	result := data.cis.microsoft_365_foundations.v6_0_0.control_2_4_2.result with input as {
		"atp_strict_rule_found": true,
		"atp_strict_rule_state": "Enabled",
		"atp_strict_rule_sent_to": ["ceo@contoso.com", "cfo@contoso.com"],
		"atp_strict_rule_sent_to_member_of": [],
		"atp_strict_rule_recipient_domain_is": [],
		"eop_strict_rule_found": true,
		"eop_strict_rule_state": "Enabled",
		"eop_strict_rule_sent_to": ["cfo@contoso.com"],
		"eop_strict_rule_sent_to_member_of": [],
		"eop_strict_rule_recipient_domain_is": [],
	}
	result.compliant == false
}

# --- Non-compliant: disabled rule ---

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
	result.details.atp_strict_rule_scoped == false
}

# --- Non-compliant: unscoped (both found and enabled, but no recipients at all) ---

test_non_compliant_unscoped if {
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

# --- Non-compliant: rule missing entirely ---

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