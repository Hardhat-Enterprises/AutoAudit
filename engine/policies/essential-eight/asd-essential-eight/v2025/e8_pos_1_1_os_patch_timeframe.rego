# METADATA
# title: Essential Eight - Operating system patches applied within required timeframe
# description: |
#   Checks whether Intune Windows Update for Business configuration profiles
#   enforce installation of quality updates within the Essential Eight ML1
#   timeframe of two weeks.
#   Evaluates the weakest update ring: deferral, deadline and grace period are
#   summed by the collector to give the maximum days before an update is active.
#   A mode that installs updates without forcing a restart only satisfies the
#   control where a non-zero deadline is configured, since most quality updates
#   require a restart to complete.
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

# Modes that install quality updates without user interaction.
ENFORCING_UPDATE_MODES := {"auto_install", "auto_install_and_reboot"}

# Modes that also force the restart most quality updates require to complete.
REBOOT_ENFORCING_MODES := {"auto_install_and_reboot"}

# Installing an update is not the same as applying it. Where the configured mode
# does not restart the device, the update can remain pending indefinitely unless
# a deadline is set, since the deadline is what forces the restart.
default restart_enforced := false

restart_enforced if {
	REBOOT_ENFORCING_MODES[input.automatic_update_mode]
}

restart_enforced if {
	input.automatic_update_mode == "auto_install"
	input.quality_updates_deadline_days > 0
}

default is_compliant := false

is_compliant if {
	input.profiles_found > 0
	not input.quality_updates_paused
	restart_enforced
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
		"restart_enforced": restart_enforced,
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
	"Profile '%s' installs updates but does not enforce a restart and sets no deadline, so updates requiring a restart may remain pending indefinitely",
	[input.weakest_profile_name],
) if {
	input.profiles_found > 0
	not input.quality_updates_paused
	ENFORCING_UPDATE_MODES[input.automatic_update_mode]
	not restart_enforced
}

message := sprintf(
	"Profile '%s' allows %d days before updates are active, exceeding the Essential Eight maximum of %d",
	[input.weakest_profile_name, input.days_to_active, MAX_DAYS_TO_ACTIVE],
) if {
	input.profiles_found > 0
	not input.quality_updates_paused
	restart_enforced
	input.days_to_active > MAX_DAYS_TO_ACTIVE
}

default message := "Unable to evaluate operating system patching: no update configuration data available"
