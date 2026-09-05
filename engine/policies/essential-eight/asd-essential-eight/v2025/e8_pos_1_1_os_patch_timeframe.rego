# METADATA
# title: Essential Eight - Operating system patches applied within required timeframe
# description: |
#   Checks whether Intune Windows Update for Business configuration profiles
#   enforce installation of quality updates within the Essential Eight ML1
#   timeframe of two weeks.
#   Evaluates the weakest update ring: deferral, deadline and grace period are
#   summed by the collector to give the maximum days before an update is active.
#   Research reference: 26T2-SEC-KS-001
# related_resources:
# - ref: https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/essential-eight
#   description: ASD Essential Eight Maturity Model
# custom:
#   control_id: E8-POS-1.1
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: high
#   service: Intune
#   maturity_level: ML1
#   requires_permissions:
#   - DeviceManagementConfiguration.Read.All

package essential_eight.asd_essential_eight.v2025.control_e8_pos_1_1

import rego.v1

MAX_DAYS_TO_ACTIVE := 14

ENFORCING_UPDATE_MODES := {"auto_install", "auto_install_and_reboot"}

default is_compliant := false

is_compliant if {
	input.profiles_found > 0
	not input.quality_updates_paused
	ENFORCING_UPDATE_MODES[input.automatic_update_mode]
	input.days_to_active <= MAX_DAYS_TO_ACTIVE
}

result := {
	"compliant": is_compliant,
	"message": message,
	"details": {
		"profiles_found": input.profiles_found,
		"weakest_profile_name": input.weakest_profile_name,
		"quality_updates_deferral_days": input.quality_updates_deferral_days,
		"quality_updates_deadline_days": input.quality_updates_deadline_days,
		"deadline_grace_period_days": input.deadline_grace_period_days,
		"days_to_active": input.days_to_active,
		"quality_updates_paused": input.quality_updates_paused,
		"automatic_update_mode": input.automatic_update_mode,
		"threshold": MAX_DAYS_TO_ACTIVE,
		"threshold_exceeded": input.days_to_active > MAX_DAYS_TO_ACTIVE,
	},
}

message := "No Windows Update for Business profile detected - tenant may be managed by Windows Autopatch, manual verification required" if {
	input.profiles_found == 0
}

message := sprintf(
	"Operating system updates are enforced within %d days on the weakest ring '%s'",
	[input.days_to_active, input.weakest_profile_name],
) if {
	input.profiles_found > 0
	is_compliant == true
}

message := sprintf(
	"Quality updates are paused on profile '%s'",
	[input.weakest_profile_name],
) if {
	input.profiles_found > 0
	input.quality_updates_paused
}

message := sprintf(
	"Profile '%s' does not enforce automatic installation (update mode: %s)",
	[input.weakest_profile_name, input.automatic_update_mode],
) if {
	input.profiles_found > 0
	not input.quality_updates_paused
	not ENFORCING_UPDATE_MODES[input.automatic_update_mode]
}

message := sprintf(
	"Profile '%s' allows %d days before updates are active, exceeding the Essential Eight maximum of %d",
	[input.weakest_profile_name, input.days_to_active, MAX_DAYS_TO_ACTIVE],
) if {
	input.profiles_found > 0
	not input.quality_updates_paused
	ENFORCING_UPDATE_MODES[input.automatic_update_mode]
	input.days_to_active > MAX_DAYS_TO_ACTIVE
}

default message := "Unable to evaluate operating system patching: no update configuration data available"
