# METADATA
# title: Ensure Use of Only Fully Supported Browsers and Email Clients (GCP)
# description: |
#   Organisations must ensure only fully supported browsers and email clients are allowed to execute
#   in the enterprise, using only the latest version provided through the vendor. This is enforced via
#   Chrome Browser Cloud Management (CBCM) minimum version and forced update settings, alongside Google
#   Workspace client access controls that disable legacy IMAP/POP protocols where not required and
#   enforce modern authentication for email access.
#   Policy scope (OU/group) and coverage must be confirmed, and a time-stamped compliance report showing
#   the device/user population meets the minimum version requirement must be provided as evidence the
#   policy is actively enforced.
# related_resources:
# - ref: https://support.google.com/chrome/a/answer/9027986
#   description: Chrome Browser Cloud Management Documentation
# - ref: https://support.google.com/a/answer/105694
#   description: Google Workspace Email Client Access Controls Documentation
# custom:
#   control_id: CIS-9.1
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   severity: medium
#   service: Chrome Browser Cloud Management / Google Workspace
#   requires_permissions:
#   - chrome.policies.get
#   - chrome.reports.get
#   - admin.directory.orgunit.readonly
#   - admin.directory.group.readonly

package cis.gcp_foundations.v2_0_0.control_9_1

import rego.v1

# Default result 
default result := {
	"compliant": false,
	"message": "Evaluation failed: insufficient data to verify that fully supported, up-to-date browsers and email clients are running",
	"details": {},
}

default compliant := false

# -----------------------
# Compliance Logic 
# -----------------------
compliant if {
	browser_policy_configured
	email_client_policy_configured
	policy_scope_defined
	compliance_evidence_recent
}

# the policy view should have minimum browser version enforced with 
# auto-updates active
browser_policy_configured if {
	input.minimum_browser_version != ""
	input.browser_auto_update_enforced == true
}

# legacy mail protocols and weak authentication are common entry points for
# credential attacks - both must be restricted before the client can
# be considered fully supported
email_client_policy_configured if {
	input.legacy_protocols_restricted == true
	input.modern_auth_required == true
}

# scope must be explicit 
policy_scope_defined if {
	input.policy_scope_type != ""
	input.policy_scope_identifier != ""
}

# the policy must be shown in active use via a recent, dated report
compliance_evidence_recent if {
	input.compliance_report_date != ""
	input.compliance_report_within_review_window == true
}

# -----------------------
# Result Output 
# -----------------------
result := output if {
	non_compliant_clients := get_array(input, "non_compliant_clients")

	output := {
		"compliant": compliant,
		"message": generate_message,
		"affected_resources": non_compliant_clients,
		"details": {
			"minimum_browser_version": input.minimum_browser_version,
			"browser_auto_update_enforced": input.browser_auto_update_enforced,
			"legacy_protocols_restricted": input.legacy_protocols_restricted,
			"modern_auth_required": input.modern_auth_required,
			"policy_scope_type": input.policy_scope_type,
			"policy_scope_identifier": input.policy_scope_identifier,
			"compliance_report_date": input.compliance_report_date,
			"compliance_report_within_review_window": input.compliance_report_within_review_window,
			"non_compliant_clients_count": count(non_compliant_clients),
			"requires_example_evidence": true,
		}
	}
}

# -----------------------
# Message Logic 
# -----------------------
generate_message := msg if {
	not browser_policy_configured
	msg := "FAIL: Minimum browser version or auto-update enforcement is not configured."
}

generate_message := msg if {
	browser_policy_configured
	not email_client_policy_configured
	msg := "FAIL: Legacy email client protocols are not restricted or modern authentication is not enforced."
}

generate_message := msg if {
	browser_policy_configured
	email_client_policy_configured
	not policy_scope_defined
	msg := "INCONCLUSIVE: Policy configuration evidence does not clearly show the OU or group scope it applies to."
}

generate_message := msg if {
	browser_policy_configured
	email_client_policy_configured
	policy_scope_defined
	not compliance_evidence_recent
	msg := "INCONCLUSIVE: No recent, time-stamped compliance report found showing the policy is actively enforced."
}

generate_message := msg if {
	compliant
	msg := "PASS: Minimum browser version and auto-update enforcement are configured, legacy email client access is restricted, policy scope is confirmed, and a recent compliance report verifies the policy is operating."
}

# -----------------------
# Helper Functions 
# -----------------------
get_array(obj, key) := value if {
	value := obj[key]
} else := []
