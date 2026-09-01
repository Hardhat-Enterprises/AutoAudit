# METADATA
# title: Essential Eight - Regular backups performed, current, restored, and access restricted
# description: |
#   Checks whether Exchange, SharePoint, and OneDrive for Business are covered
#   by an active Microsoft 365 Backup Storage protection policy, whether each
#   has produced a restore point within the last 24 hours, whether at least
#   one restore session has been recorded within the last 12 months as
#   evidence restoration has been exercised, and whether membership in the
#   three backup admin roles is limited to an appropriate set of users.
#   The 24 hour and 12 month thresholds, and the backup admin member count
#   threshold, are AutoAudit's own default implementation decisions, not
#   ACSC-mandated figures, since current ACSC guidance does not prescribe them.
#   Research reference: 26T2-SEC-EG-001, 26T2-SEC-EG-002
# custom:
#   control_id: E8-BAK-1.1
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: high
#   service: M365BackupStorage
#   requires_permissions:
#   - BackupRestore-Restore.Read.All
#   - RoleManagement.Read.Directory

package essential_eight.asd_essential_eight.v2025.control_e8_bak_1_1

import rego.v1

# Default implementation thresholds. Not ACSC-mandated figures, see METADATA.
MAX_BACKUP_ADMIN_ACCOUNTS := 5

RESTORE_SESSION_WINDOW_NS := 12 * 30 * 24 * 60 * 60 * 1000000000 # ~12 months

REQUIRED_SERVICES := {"Exchange", "SharePoint", "OneDrive"}

# Maps the @odata.type suffixes returned by the collector to a service name.
protection_policy_service_map := {
	"exchangeProtectionPolicy": "Exchange",
	"sharePointProtectionPolicy": "SharePoint",
	"oneDriveForBusinessProtectionPolicy": "OneDrive",
}

restore_point_service_map := {
	"mailboxProtectionUnit": "Exchange",
	"siteProtectionUnit": "SharePoint",
	"driveProtectionUnit": "OneDrive",
}

# --- Protection policies: one active policy per required service ---

active_policy_services := {service |
	some p in input.protection_policies
	p.status == "active"
	service := protection_policy_service_map[p.service]
}

services_missing_active_policy := REQUIRED_SERVICES - active_policy_services

# --- Restore points: at least one recent restore point per required service ---
# input.recent_restore_points is already filtered to the last 24 hours by the collector.

services_with_recent_restore_point := {service |
	some rp in input.recent_restore_points
	service := restore_point_service_map[rp.protectionUnitType]
}

services_missing_recent_restore_point := REQUIRED_SERVICES - services_with_recent_restore_point

# --- Restore sessions: at least one within the last 12 months ---

recent_restore_sessions := [s |
	some s in input.restore_sessions
	s.createdDateTime != null
	created_ns := time.parse_rfc3339_ns(s.createdDateTime)
	created_ns >= time.now_ns() - RESTORE_SESSION_WINDOW_NS
]

has_recent_restore_session if count(recent_restore_sessions) > 0

default has_recent_restore_session := false

# --- Backup admin roles: membership within threshold ---

total_backup_admin_members := sum([count(r.members) |
	some r in input.backup_admin_roles
])

backup_admin_access_excessive if total_backup_admin_members > MAX_BACKUP_ADMIN_ACCOUNTS

default backup_admin_access_excessive := false

# --- Overall compliance ---

is_compliant if {
	count(services_missing_active_policy) == 0
	count(services_missing_recent_restore_point) == 0
	has_recent_restore_session
	not backup_admin_access_excessive
}

default is_compliant := false

result := {
	"compliant": is_compliant,
	"message": message,
	"details": {
		"services_missing_active_policy": services_missing_active_policy,
		"services_missing_recent_restore_point": services_missing_recent_restore_point,
		"has_recent_restore_session": has_recent_restore_session,
		"restore_session_count": count(input.restore_sessions),
		"total_backup_admin_members": total_backup_admin_members,
		"backup_admin_threshold": MAX_BACKUP_ADMIN_ACCOUNTS,
		"backup_admin_access_excessive": backup_admin_access_excessive,
		"backup_admin_roles_not_found": input.roles_not_found,
	},
}

message := "Regular backups are compliant: all services have active, current protection, a recent restore session exists, and backup admin access is appropriately restricted" if {
	is_compliant
}

message := sprintf(
	"Regular backups non-compliant: no active protection policy for %v",
	[services_missing_active_policy],
) if {
	count(services_missing_active_policy) > 0
}

message := sprintf(
	"Regular backups non-compliant: no restore point within the last 24 hours for %v",
	[services_missing_recent_restore_point],
) if {
	count(services_missing_active_policy) == 0
	count(services_missing_recent_restore_point) > 0
}

message := "Regular backups non-compliant: no restore session recorded within the last 12 months" if {
	count(services_missing_active_policy) == 0
	count(services_missing_recent_restore_point) == 0
	not has_recent_restore_session
}

message := sprintf(
	"Regular backups non-compliant: backup admin role membership (%d) exceeds the threshold of %d",
	[total_backup_admin_members, MAX_BACKUP_ADMIN_ACCOUNTS],
) if {
	count(services_missing_active_policy) == 0
	count(services_missing_recent_restore_point) == 0
	has_recent_restore_session
	backup_admin_access_excessive
}

default message := "Unable to evaluate Regular Backups: no backup data available"
