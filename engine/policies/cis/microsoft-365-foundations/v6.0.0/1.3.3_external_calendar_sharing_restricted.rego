# METADATA
# title: Ensure 'External sharing' of calendars is not available
# description: |
#   External calendar sharing policies should not be enabled. Enabled policies
#   that define external domains allow free/busy details to be shared outside
#   the organization. The Default Sharing Policy must also be disabled.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-1.3.3
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_1_3_3

default result := {"compliant": false, "message": "Evaluation failed"}

result := output if {
	policies_allowing_external := object.get(input, "policies_allowing_external", [])

	enabled_external_policies := [p |
		some p in policies_allowing_external
		p.enabled == true
	]

	# CIS 1.3.3 audits the Default Sharing Policy's Enabled flag directly and
	# requires it to be false. The collector only adds a policy to
	# policies_allowing_external when it defines domains, so an enabled Default
	# Sharing Policy with no domains must still be caught here.
	default_policy_enabled := [input.default_policy |
		input.default_policy.Enabled == true
	]

	total_violations := count(enabled_external_policies) + count(default_policy_enabled)
	compliant := total_violations == 0

	output := {
		"compliant": compliant,
		"message": generate_message(compliant, enabled_external_policies, count(default_policy_enabled) > 0),
		"affected_resources": generate_affected_resources(enabled_external_policies, default_policy_enabled),
		"details": {
			"policies_allowing_external": policies_allowing_external,
			"enabled_external_policies": enabled_external_policies,
			"default_policy_enabled": count(default_policy_enabled) > 0,
		},
	}
}

generate_message(true, _, _) := "No sharing policies allow external calendar sharing and the Default Sharing Policy is disabled"

generate_message(false, enabled_external_policies, _) := msg if {
	count(enabled_external_policies) > 0
	msg := sprintf("%d sharing policy(ies) allow external calendar sharing", [count(enabled_external_policies)])
}

generate_message(false, enabled_external_policies, true) := msg if {
	count(enabled_external_policies) == 0
	msg := "The Default Sharing Policy is enabled; the CIS benchmark requires it to be disabled"
}

generate_affected_resources(enabled_external_policies, default_policy_enabled) := resources if {
	external_names := [p.name | some p in enabled_external_policies]
	default_names := [p.Name | some p in default_policy_enabled]
	resources := array.concat(external_names, default_names)
}