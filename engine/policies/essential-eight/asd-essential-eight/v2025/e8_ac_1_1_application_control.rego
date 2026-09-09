# METADATA
# title: Essential Eight - Application Control deployed and enforced on workstations
# description: |
#   Checks whether an Intune application control policy is deployed to workstations
#   and configured to enforce rather than audit, as required by the Essential Eight
#   Application Control mitigation strategy at ML1.
#   Reads either the legacy Application control profile (appLockerApplicationControl)
#   or a modern App Control for Business policy. Evaluates the weakest policy: a
#   narrowly scoped, audit-only or reputation-only policy undermines the control
#   even where stronger policies exist.
#   An assignment record alone is not treated as deployment. Only a tenant-wide
#   assignment without exclusions establishes coverage; a group-scoped or excluded
#   assignment returns insufficient evidence, since confirming which workstations
#   are reached requires device inventory rather than policy configuration.
#   Coverage of the seven ML1 executable categories and of user profile and
#   temporary folder paths is likewise not derivable from Graph configuration and
#   is tracked separately as E8-AC-1.2 and E8-AC-1.3.
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

ENFORCING_STATES := {"enforced"}

# Only a tenant-wide assignment demonstrates that the workstations in scope
# receive the policy. Group targeting and exclusions both reduce coverage to a
# subset that cannot be measured from configuration alone.
default deployment_confirmed := false

deployment_confirmed if {
	input.assignment_scope == "all_devices"
	input.has_exclusions == false
}

default coverage_unestablished := false

coverage_unestablished if {
	input.assignment_scope != "none"
	not deployment_confirmed
}

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
	deployment_confirmed
	ENFORCING_STATES[input.configured_enforcement_state]
	not reputation_only_trust
}

# Absence of evidence is not evidence of compliance, and it is not proof of
# failure either. Where no policy is returned, the configured state cannot be
# interpreted, or deployment coverage cannot be established, the control reports
# insufficient evidence.
default assessment_state := "non_compliant"

assessment_state := "compliant" if {
	is_compliant
}

assessment_state := "insufficient_evidence" if {
	input.policies_found == 0
}

assessment_state := "insufficient_evidence" if {
	input.policies_found > 0
	input.configured_enforcement_state == "unknown"
}

assessment_state := "insufficient_evidence" if {
	input.policies_found > 0
	ENFORCING_STATES[input.configured_enforcement_state]
	not reputation_only_trust
	coverage_unestablished
}

result := {
	"compliant": is_compliant,
	"message": message,
	"details": {
		"assessment_state": assessment_state,
		"policies_found": input.policies_found,
		"weakest_policy_name": input.weakest_policy_name,
		"graph_source_type": input.graph_source_type,
		"graph_policy_id": input.graph_policy_id,
		"configured_enforcement_state": input.configured_enforcement_state,
		"trust_reputation": input.trust_reputation,
		"trust_managed_installer": input.trust_managed_installer,
		"assignment_scope": input.assignment_scope,
		"has_exclusions": input.has_exclusions,
		"deployment_confirmed": deployment_confirmed,
		"effective_device_state_verified": input.effective_device_state_verified,
		"reputation_only_trust": reputation_only_trust,
	},
}

message := "No Intune application control policy detected - application control may be enforced by another mechanism, manual verification required" if {
	input.policies_found == 0
}

message := sprintf(
	"Application control is enforced by policy '%s', assigned tenant-wide",
	[input.weakest_policy_name],
) if {
	input.policies_found > 0
	is_compliant == true
}

message := sprintf(
	"Policy '%s' exists but is not assigned to any group or device, so it is not deployed",
	[input.weakest_policy_name],
) if {
	input.policies_found > 0
	input.assignment_scope == "none"
}

message := sprintf(
	"Configured state of policy '%s' could not be interpreted - manual verification required",
	[input.weakest_policy_name],
) if {
	input.policies_found > 0
	input.assignment_scope != "none"
	input.configured_enforcement_state == "unknown"
}

message := sprintf(
	"Policy '%s' is not enforced (state: %s) - applications are permitted to run",
	[input.weakest_policy_name, input.configured_enforcement_state],
) if {
	input.policies_found > 0
	input.assignment_scope != "none"
	not ENFORCING_STATES[input.configured_enforcement_state]
	input.configured_enforcement_state != "unknown"
}

message := sprintf(
	"Policy '%s' trusts applications on reputation alone, which is not an organisation approved set",
	[input.weakest_policy_name],
) if {
	input.policies_found > 0
	input.assignment_scope != "none"
	ENFORCING_STATES[input.configured_enforcement_state]
	reputation_only_trust
}

message := sprintf(
	"Policy '%s' is enforced but assigned with scope '%s', so coverage of the required workstations cannot be established from configuration - manual verification required",
	[input.weakest_policy_name, input.assignment_scope],
) if {
	input.policies_found > 0
	ENFORCING_STATES[input.configured_enforcement_state]
	not reputation_only_trust
	coverage_unestablished
}

default message := "Unable to evaluate application control: no policy configuration data available"
