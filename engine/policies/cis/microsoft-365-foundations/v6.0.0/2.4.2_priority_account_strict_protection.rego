# METADATA
# title: Ensure Priority accounts have 'Strict protection' presets applied
# description: Ensure the built-in Strict Preset Security Policy is enabled and scoped to specific recipients (priority accounts/groups) for both Defender for Office 365 (ATP) and Exchange Online Protection (EOP).
# custom:
#   control_id: CIS-2.4.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: high
#   service: Defender
#   requires_permissions:
#   - Exchange.ManageAsApp

package cis.microsoft_365_foundations.v6_0_0.control_2_4_2

import rego.v1

default result := {
	"compliant": false,
	"message": "Unable to determine Strict Preset Security Policy configuration",
	"details": {},
}

# --- ATP (Defender for Office 365) strict preset rule ---

default atp_ok := false

atp_ok if {
	input.atp_strict_rule_found == true
	input.atp_strict_rule_state == "Enabled"
	atp_has_target
}

atp_has_target if count(object.get(input, "atp_strict_rule_sent_to", [])) > 0

atp_has_target if count(object.get(input, "atp_strict_rule_sent_to_member_of", [])) > 0

atp_has_target if count(object.get(input, "atp_strict_rule_recipient_domain_is", [])) > 0

# --- EOP (Exchange Online Protection) strict preset rule ---

default eop_ok := false

eop_ok if {
	input.eop_strict_rule_found == true
	input.eop_strict_rule_state == "Enabled"
	eop_has_target
}

eop_has_target if count(object.get(input, "eop_strict_rule_sent_to", [])) > 0

eop_has_target if count(object.get(input, "eop_strict_rule_sent_to_member_of", [])) > 0

eop_has_target if count(object.get(input, "eop_strict_rule_recipient_domain_is", [])) > 0

# --- Cross-check: both rules must protect the SAME priority accounts/groups ---
#
# atp_ok and eop_ok on their own only prove each rule is scoped to *some*
# recipient independently. Two rules scoped to different accounts (e.g.
# ATP -> ceo@contoso.com, EOP -> cfo@contoso.com) would both satisfy that,
# but neither account actually receives the full Strict preset. Comparing
# the recipient targets as sets ensures the same accounts/groups are
# covered by both ATP and EOP, matching how the built-in preset is meant
# to be configured (one policy, same scope, applied to both protections).

to_set(arr) := {x | some x in arr}

default same_recipients := false

same_recipients if {
	to_set(object.get(input, "atp_strict_rule_sent_to", [])) == to_set(object.get(input, "eop_strict_rule_sent_to", []))
	to_set(object.get(input, "atp_strict_rule_sent_to_member_of", [])) == to_set(object.get(input, "eop_strict_rule_sent_to_member_of", []))
	to_set(object.get(input, "atp_strict_rule_recipient_domain_is", [])) == to_set(object.get(input, "eop_strict_rule_recipient_domain_is", []))
}

# --- Overall compliance: both rules must exist, be enabled, be scoped, AND
#     protect the same priority accounts/groups ---

default compliant := false

compliant if {
	atp_ok
	eop_ok
	same_recipients
}

result := output if {
	is_boolean(object.get(input, "atp_strict_rule_found", null))
	is_boolean(object.get(input, "eop_strict_rule_found", null))

	output := {
		"compliant": compliant,
		"message": generate_message(compliant),
		"details": {
			"atp_strict_rule_found": input.atp_strict_rule_found,
			"atp_strict_rule_state": object.get(input, "atp_strict_rule_state", null),
			"atp_strict_rule_scoped": atp_ok,
			"eop_strict_rule_found": input.eop_strict_rule_found,
			"eop_strict_rule_state": object.get(input, "eop_strict_rule_state", null),
			"eop_strict_rule_scoped": eop_ok,
			"same_priority_accounts_covered": same_recipients,
		},
	}
}

generate_message(true) := "Strict Preset Security Policy is enabled and scoped to the same priority accounts/groups for both Defender (ATP) and Exchange Online Protection (EOP)"

generate_message(false) := "Strict Preset Security Policy is missing, disabled, not scoped to specific recipients, or scoped to different recipients between Defender (ATP) and Exchange Online Protection (EOP)"