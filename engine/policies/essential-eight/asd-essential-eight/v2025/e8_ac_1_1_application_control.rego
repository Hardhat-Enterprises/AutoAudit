# METADATA
# title: Essential Eight - Application Control deployed and enforced on workstations
# description: |
#   Checks whether Intune App Control for Business policies are deployed and
#   operating in an enforced state rather than audit only, as required by the
#   Essential Eight Application Control mitigation strategy at ML1.
#   Evaluates the weakest policy: an unassigned, audit-only or reputation-only
#   policy undermines the control even where stronger policies exist.
#   Research reference: 26T2-SEC-KHS-001, 26T2-SEC-TD-001
# related_resources:
# - ref: https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight
#   description: ASD Essential Eight Maturity Model
# - ref: https://learn.microsoft.com/en-us/intune/device-configuration/endpoint-security/manage-app-control
#   description: Manage approved apps with App Control for Business in Microsoft Intune
# custom:
#   control_id: E8-AC-1.1
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: high
#   service: Intune
#   maturity_level: ML1
#   requires_permissions:
#   - DeviceManagementConfiguration.Read.All

package essential_eight.asd_essential_eight.v2025.control_e8_ac_1_1

import rego.v1

ENFORCING_MODES := {"enforced"}

# The Essential Eight requires execution to be limited to an organisation
# approved set. Trusting applications on reputation alone, via the Microsoft
# Intelligent Security Graph, is not an organisation approved set.
default reputation_only_trust := false

reputation_only_trust if {
	input.trust_reputation == true
	input.trust_managed_installer == false
}

default is_compliant := false

is_compliant if {
	input.policies_found > 0
	input.assigned == true
	ENFORCING_MODES[input.enforcement_mode]
	not reputation_only_trust
}

result := {
	"compliant": is_compliant,
	"message": message,
	"details": {
		"policies_found": input.policies_found,
		"weakest_policy_name": input.weakest_policy_name,
		"policy_format": input.policy_format,
		"enforcement_mode": input.enforcement_mode,
		"trust_reputation": input.trust_reputation,
		"trust_managed_installer": input.trust_managed_installer,
		"assigned": input.assigned,
		"reputation_only_trust": reputation_only_trust,
	},
}

message := "No App Control for Business policy detected - application control may be enforced outside Intune, manual verification required" if {
	input.policies_found == 0
}

message := sprintf(
	"Application control is enforced by policy '%s'",
	[input.weakest_policy_name],
) if {
	input.policies_found > 0
	is_compliant == true
}

message := sprintf(
	"Policy '%s' exists but is not assigned to any group, so it is not deployed",
	[input.weakest_policy_name],
) if {
	input.policies_found > 0
	input.assigned == false
}

message := sprintf(
	"Policy '%s' is not enforced (mode: %s) - applications are permitted to run",
	[input.weakest_policy_name, input.enforcement_mode],
) if {
	input.policies_found > 0
	input.assigned == true
	not ENFORCING_MODES[input.enforcement_mode]
}

message := sprintf(
	"Policy '%s' trusts applications on reputation alone, which is not an organisation approved set",
	[input.weakest_policy_name],
) if {
	input.policies_found > 0
	input.assigned == true
	ENFORCING_MODES[input.enforcement_mode]
	reputation_only_trust
}

default message := "Unable to evaluate application control: no policy configuration data available"
