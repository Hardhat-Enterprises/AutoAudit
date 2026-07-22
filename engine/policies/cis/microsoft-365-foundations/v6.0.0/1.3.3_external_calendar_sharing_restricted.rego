# METADATA
# title: Ensure 'External sharing' of calendars is not available
# description: |
#   External calendar sharing policies should not be enabled. Enabled policies
#   that define external domains allow free/busy details to be shared outside
#   the organization.
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

	compliant := count(enabled_external_policies) == 0

	output := {
		"compliant": compliant,
		"message": generate_message(compliant, enabled_external_policies),
		"affected_resources": generate_affected_resources(enabled_external_policies),
		"details": {
			"policies_allowing_external": policies_allowing_external,
			"enabled_external_policies": enabled_external_policies,
		},
	}
}

generate_message(true, _) := "No sharing policies allow external calendar sharing"

generate_message(false, enabled_external_policies) := msg if {
	count(enabled_external_policies) > 0
	msg := sprintf("%d sharing policy(ies) allow external calendar sharing", [count(enabled_external_policies)])
}

generate_affected_resources(enabled_external_policies) := [p.name |
	some p in enabled_external_policies
]
