# METADATA
# title: Ensure Priority account protection is enabled and configured
# description: |
#  Priority account protection applies additional safeguards (enhanced sign-in security,
#  targeted alerts) to accounts tagged as priority (VIP) accounts, such as
#  executives or other high value targets. The tenant-wide protection setting
#  must be enabled, at least one account must be tagged as a priority account,
#  and alert policies must be configured for each priority account.
#
#  This policy is currently inactive and requires alert policy configuration records
#  that are not yet available, pending the implementation of Connect-IPPSSession functionality.
# 
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.4.1
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Defender
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_4_1

default result := {"compliant": false, "message": "Evaluation failed", "details": {}}

protection_enabled := object.get(input, "protection_enabled", null)

total_priority_accounts := object.get(input, "total_priority_accounts", 0)

state := "configured" if {
	protection_enabled == true
	total_priority_accounts > 0
}

state := "enabled but unconfigured" if {
	protection_enabled == true
	total_priority_accounts <= 0
}

state := "disabled" if {
	protection_enabled == false
}

state := "unknown" if {
	protection_enabled == null
}

result := output if {
	output := {
		"compliant": state == "configured",
		"message": generate_message(state),
		"affected_resources": generate_affected_resources(state),
		"details": {
			"protection_enabled": protection_enabled,
			"total_priority_accounts": total_priority_accounts
		}
	}
}

generate_message("configured") := sprintf(
	"Priority account protection is enabled and configured with %d priority account(s)",
	[total_priority_accounts],
)

generate_message("enabled but unconfigured") := "Priority account protection is enabled, but no accounts are tagged as priority accounts"
generate_message("disabled") := "Priority account protection is not enabled"
generate_message("unknown") := "Unable to determine if Priority account protection is enabled"

generate_affected_resources("configured") := []
generate_affected_resources("enabled but unconfigured") := ["Priority accounts"]
generate_affected_resources("disabled") := ["EmailTenantSettings"]
generate_affected_resources("unknown") := ["EmailTenantSettings status unknown"]
