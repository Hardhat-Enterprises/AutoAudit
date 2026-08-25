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

# Defaults below matter: atp_ok/eop_ok are read directly into the details
# object further down. Without a default, a rule that simply fails to
# match (e.g. found but disabled) would leave atp_ok undefined, which
# would make the whole `result` object construction fail and silently
# fall through to the "unable to determine" default instead of correctly
# reporting a known non-compliant state.
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

# --- Overall compliance: both rules must exist, be enabled, and be scoped ---

default compliant := false

compliant if {
	atp_ok
	eop_ok
}

# The guard below requires both "*_found" flags to actually be booleans
# (i.e. the collector ran and returned real evidence). If they are missing
# or null, this rule body fails and `result` falls through to the
# fail-closed default above instead of silently evaluating `compliant`
# against undefined data.
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
		},
	}
}

generate_message(true) := "Strict Preset Security Policy is enabled and scoped to specific recipients for both Defender (ATP) and Exchange Online Protection (EOP)"

generate_message(false) := "Strict Preset Security Policy is missing, disabled, or not scoped to specific recipients for Defender (ATP) and/or Exchange Online Protection (EOP)"