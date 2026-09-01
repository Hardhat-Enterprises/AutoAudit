package essential_eight.asd_essential_eight.v2025.test_e8_bak_1_1

import rego.v1

# NOTE: recent_restore_point and recent_restore_session dates below are
# illustrative fixed dates rather than computed relative to test run time.
# "recent_restore_point" tests use a date close to when this file was
# written; "recent_restore_session" tests use a date within the last few
# months of that. These will need refreshing if the fixed dates fall outside
# the 24 hour / 12 month windows by the time the tests are actually run.

test_compliant_all_conditions_met if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_bak_1_1.result with input as {
		"protection_policies": [
			{"id": "p1", "service": "exchangeProtectionPolicy", "status": "active"},
			{"id": "p2", "service": "sharePointProtectionPolicy", "status": "active"},
			{"id": "p3", "service": "oneDriveForBusinessProtectionPolicy", "status": "active"},
		],
		"recent_restore_points": [
			{"id": "rp1", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "mailboxProtectionUnit"},
			{"id": "rp2", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "siteProtectionUnit"},
			{"id": "rp3", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "driveProtectionUnit"},
		],
		"restore_sessions": [
			{"id": "s1", "status": "succeeded", "createdDateTime": "2026-06-01T00:00:00Z"},
		],
		"backup_admin_roles": [
			{"role_name": "Microsoft 365 Backup Administrator", "member_count": 2, "members": [{"id": "1"}, {"id": "2"}]},
			{"role_name": "SharePoint Backup Administrator", "member_count": 1, "members": [{"id": "3"}]},
			{"role_name": "Exchange Backup Administrator", "member_count": 0, "members": []},
		],
		"roles_not_found": [],
	}
	result.compliant == true
	result.details.services_missing_active_policy == set()
	result.details.services_missing_recent_restore_point == set()
	result.details.has_recent_restore_session == true
	result.details.backup_admin_access_excessive == false
}

test_non_compliant_missing_active_policy if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_bak_1_1.result with input as {
		"protection_policies": [
			{"id": "p1", "service": "exchangeProtectionPolicy", "status": "active"},
			{"id": "p2", "service": "sharePointProtectionPolicy", "status": "inactive"},
			{"id": "p3", "service": "oneDriveForBusinessProtectionPolicy", "status": "active"},
		],
		"recent_restore_points": [
			{"id": "rp1", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "mailboxProtectionUnit"},
			{"id": "rp3", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "driveProtectionUnit"},
		],
		"restore_sessions": [
			{"id": "s1", "status": "succeeded", "createdDateTime": "2026-06-01T00:00:00Z"},
		],
		"backup_admin_roles": [
			{"role_name": "Microsoft 365 Backup Administrator", "member_count": 1, "members": [{"id": "1"}]},
			{"role_name": "SharePoint Backup Administrator", "member_count": 0, "members": []},
			{"role_name": "Exchange Backup Administrator", "member_count": 0, "members": []},
		],
		"roles_not_found": [],
	}
	result.compliant == false
	"SharePoint" in result.details.services_missing_active_policy
	contains(result.message, "no active protection policy")
}

test_non_compliant_missing_recent_restore_point if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_bak_1_1.result with input as {
		"protection_policies": [
			{"id": "p1", "service": "exchangeProtectionPolicy", "status": "active"},
			{"id": "p2", "service": "sharePointProtectionPolicy", "status": "active"},
			{"id": "p3", "service": "oneDriveForBusinessProtectionPolicy", "status": "active"},
		],
		"recent_restore_points": [
			{"id": "rp1", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "mailboxProtectionUnit"},
			{"id": "rp2", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "siteProtectionUnit"},
		],
		"restore_sessions": [
			{"id": "s1", "status": "succeeded", "createdDateTime": "2026-06-01T00:00:00Z"},
		],
		"backup_admin_roles": [
			{"role_name": "Microsoft 365 Backup Administrator", "member_count": 1, "members": [{"id": "1"}]},
			{"role_name": "SharePoint Backup Administrator", "member_count": 0, "members": []},
			{"role_name": "Exchange Backup Administrator", "member_count": 0, "members": []},
		],
		"roles_not_found": [],
	}
	result.compliant == false
	"OneDrive" in result.details.services_missing_recent_restore_point
	contains(result.message, "no restore point within the last 24 hours")
}

test_non_compliant_no_restore_session if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_bak_1_1.result with input as {
		"protection_policies": [
			{"id": "p1", "service": "exchangeProtectionPolicy", "status": "active"},
			{"id": "p2", "service": "sharePointProtectionPolicy", "status": "active"},
			{"id": "p3", "service": "oneDriveForBusinessProtectionPolicy", "status": "active"},
		],
		"recent_restore_points": [
			{"id": "rp1", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "mailboxProtectionUnit"},
			{"id": "rp2", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "siteProtectionUnit"},
			{"id": "rp3", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "driveProtectionUnit"},
		],
		"restore_sessions": [],
		"backup_admin_roles": [
			{"role_name": "Microsoft 365 Backup Administrator", "member_count": 1, "members": [{"id": "1"}]},
			{"role_name": "SharePoint Backup Administrator", "member_count": 0, "members": []},
			{"role_name": "Exchange Backup Administrator", "member_count": 0, "members": []},
		],
		"roles_not_found": [],
	}
	result.compliant == false
	result.details.has_recent_restore_session == false
	result.message == "Regular backups non-compliant: no restore session recorded within the last 12 months"
}

test_non_compliant_stale_restore_session if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_bak_1_1.result with input as {
		"protection_policies": [
			{"id": "p1", "service": "exchangeProtectionPolicy", "status": "active"},
			{"id": "p2", "service": "sharePointProtectionPolicy", "status": "active"},
			{"id": "p3", "service": "oneDriveForBusinessProtectionPolicy", "status": "active"},
		],
		"recent_restore_points": [
			{"id": "rp1", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "mailboxProtectionUnit"},
			{"id": "rp2", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "siteProtectionUnit"},
			{"id": "rp3", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "driveProtectionUnit"},
		],
		"restore_sessions": [
			{"id": "s1", "status": "succeeded", "createdDateTime": "2023-01-01T00:00:00Z"},
		],
		"backup_admin_roles": [
			{"role_name": "Microsoft 365 Backup Administrator", "member_count": 1, "members": [{"id": "1"}]},
			{"role_name": "SharePoint Backup Administrator", "member_count": 0, "members": []},
			{"role_name": "Exchange Backup Administrator", "member_count": 0, "members": []},
		],
		"roles_not_found": [],
	}
	result.compliant == false
	result.details.has_recent_restore_session == false
}

test_non_compliant_excessive_backup_admin_access if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_bak_1_1.result with input as {
		"protection_policies": [
			{"id": "p1", "service": "exchangeProtectionPolicy", "status": "active"},
			{"id": "p2", "service": "sharePointProtectionPolicy", "status": "active"},
			{"id": "p3", "service": "oneDriveForBusinessProtectionPolicy", "status": "active"},
		],
		"recent_restore_points": [
			{"id": "rp1", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "mailboxProtectionUnit"},
			{"id": "rp2", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "siteProtectionUnit"},
			{"id": "rp3", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "driveProtectionUnit"},
		],
		"restore_sessions": [
			{"id": "s1", "status": "succeeded", "createdDateTime": "2026-06-01T00:00:00Z"},
		],
		"backup_admin_roles": [
			{"role_name": "Microsoft 365 Backup Administrator", "member_count": 6, "members": [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}, {"id": "5"}, {"id": "6"}]},
			{"role_name": "SharePoint Backup Administrator", "member_count": 0, "members": []},
			{"role_name": "Exchange Backup Administrator", "member_count": 0, "members": []},
		],
		"roles_not_found": [],
	}
	result.compliant == false
	result.details.backup_admin_access_excessive == true
	result.details.total_backup_admin_members == 6
	contains(result.message, "exceeds the threshold")
}

test_compliant_at_admin_threshold if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_bak_1_1.result with input as {
		"protection_policies": [
			{"id": "p1", "service": "exchangeProtectionPolicy", "status": "active"},
			{"id": "p2", "service": "sharePointProtectionPolicy", "status": "active"},
			{"id": "p3", "service": "oneDriveForBusinessProtectionPolicy", "status": "active"},
		],
		"recent_restore_points": [
			{"id": "rp1", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "mailboxProtectionUnit"},
			{"id": "rp2", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "siteProtectionUnit"},
			{"id": "rp3", "protectionDateTime": "2026-08-19T00:00:00Z", "expirationDateTime": "2027-08-19T00:00:00Z", "protectionUnitType": "driveProtectionUnit"},
		],
		"restore_sessions": [
			{"id": "s1", "status": "succeeded", "createdDateTime": "2026-06-01T00:00:00Z"},
		],
		"backup_admin_roles": [
			{"role_name": "Microsoft 365 Backup Administrator", "member_count": 5, "members": [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}, {"id": "5"}]},
			{"role_name": "SharePoint Backup Administrator", "member_count": 0, "members": []},
			{"role_name": "Exchange Backup Administrator", "member_count": 0, "members": []},
		],
		"roles_not_found": [],
	}
	result.compliant == true
	result.details.backup_admin_access_excessive == false
}

test_non_compliant_nothing_configured if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_bak_1_1.result with input as {
		"protection_policies": [],
		"recent_restore_points": [],
		"restore_sessions": [],
		"backup_admin_roles": [],
		"roles_not_found": ["Microsoft 365 Backup Administrator", "SharePoint Backup Administrator", "Exchange Backup Administrator"],
	}
	result.compliant == false
	count(result.details.services_missing_active_policy) == 3
	result.details.backup_admin_roles_not_found == ["Microsoft 365 Backup Administrator", "SharePoint Backup Administrator", "Exchange Backup Administrator"]
}

test_result_details_structure if {
	result := data.essential_eight.asd_essential_eight.v2025.control_e8_bak_1_1.result with input as {
		"protection_policies": [
			{"id": "p1", "service": "exchangeProtectionPolicy", "status": "active"},
		],
		"recent_restore_points": [],
		"restore_sessions": [],
		"backup_admin_roles": [],
		"roles_not_found": [],
	}
	_ = result.compliant
	_ = result.message
	_ = result.details.services_missing_active_policy
	_ = result.details.services_missing_recent_restore_point
	_ = result.details.has_recent_restore_session
	_ = result.details.restore_session_count
	_ = result.details.total_backup_admin_members
	_ = result.details.backup_admin_threshold
	_ = result.details.backup_admin_access_excessive
	_ = result.details.backup_admin_roles_not_found
}
