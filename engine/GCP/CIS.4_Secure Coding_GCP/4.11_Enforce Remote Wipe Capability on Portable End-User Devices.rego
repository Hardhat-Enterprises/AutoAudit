# METADATA
# title: Enforce Remote Wipe Capability on Portable End-User Devices (GCP)
# description: |
#   Enterprise data must be capable of being remotely wiped from
#   enterprise-owned portable end-user devices when appropriate, including
#   when a device is lost or stolen or when an individual no longer
#   supports the enterprise.
#
#   Remote wipe must be supported by a documented operational process and
#   immediate identity and access revocation. A successful implementation
#   therefore requires both:
#   - Remote or corporate wipe capability
#   - IAM deprovisioning and session revocation
#
#   Google Cloud implementation uses:
#   - Google Workspace or a dedicated Mobile Device Management (MDM)
#     platform for remote wipe or corporate wipe
#   - IAM deprovisioning workflows to disable users
#   - Removal of privileged group memberships
#   - Session revocation following device loss or employee offboarding
#   - Cloud Audit Logs and administrative logs to provide traceability
#
#   The control verifies:
#   - Remote wipe capability is enabled
#   - Wipe capability is assigned to in-scope portable devices
#   - A lost-device/offboarding runbook exists
#   - Wipe and access-revocation timelines are defined
#   - Wipe execution can be demonstrated
#   - Wipe completion is recorded
#   - User accounts are disabled following the event
#   - Privileged group memberships are removed
#   - Active sessions are revoked
#   - Audit logs provide traceability
#   - Wipe and revocation actions can be correlated to an operator and time
#   - Procedures are periodically reviewed
#
# related_resources:
# - ref: https://support.google.com/a/answer/173390
#   description: Google Workspace Mobile Device Management Documentation
# - ref: https://support.google.com/a/answer/7394923
#   description: Google Workspace Remote Wipe Documentation
# - ref: https://cloud.google.com/iam/docs
#   description: Google Cloud IAM Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Documentation
#
# custom:
#   control_id: CIS-4.11
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.11
#   severity: high
#   service: Google Workspace / MDM / IAM / Cloud Audit Logs
#   asset_type: Data
#   implementation_group: 2
#   requires_permissions:
#   - admin.directory.user.readonly
#   - admin.directory.group.readonly
#   - logging.viewer
#   - iam.serviceAccounts.get
#   - resourcemanager.projects.getIamPolicy

package cis.gcp_foundations.v2_0_0.control_4_11

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient remote wipe or access revocation evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    remote_wipe_process_defined
    portable_device_scope_defined
    remote_wipe_capability_verified
    wipe_assignment_verified
    lost_device_runbook_verified
    wipe_execution_verified
    iam_revocation_verified
    session_revocation_verified
    audit_traceability_verified
    procedure_review_verified
}

# ---------------------------
# Validate Remote Wipe Process
# ---------------------------
remote_wipe_process_defined if {
    input.remote_wipe_policy_defined == true
    input.remote_wipe_conditions_defined == true
    input.remote_wipe_authority_defined == true
}

# ---------------------------
# Validate Portable Device Scope
# ---------------------------
portable_device_scope_defined if {
    input.portable_device_scope_defined == true
    input.enterprise_owned_devices_defined == true
    input.portable_device_fleet_count > 0
}

# ---------------------------
# Validate Remote Wipe Capability
# ---------------------------
remote_wipe_capability_verified if {
    input.remote_wipe_capability_enabled == true
    input.corporate_wipe_capability_enabled == true
}

# ---------------------------
# Validate Device Assignment
# ---------------------------
wipe_assignment_verified if {
    input.wipe_policy_assignment_defined == true
    input.wipe_policy_assignment_scope_defined == true
    input.in_scope_devices_enrolled == true
}

# ---------------------------
# Validate Lost Device / Offboarding Runbook
# ---------------------------
lost_device_runbook_verified if {
    input.lost_device_runbook_available == true
    input.offboarding_runbook_available == true
    input.runbook_roles_defined == true
    input.runbook_approval_date != ""
    input.runbook_last_review_date != ""
    input.wipe_timeline_defined == true
    input.access_revocation_timeline_defined == true
}

# ---------------------------
# Validate Wipe Execution
# ---------------------------
wipe_execution_verified if {
    input.wipe_test_performed == true
    input.wipe_test_device != ""
    input.wipe_action_log_available == true
    input.wipe_action_timestamp != ""
    input.wipe_action_outcome == "COMPLETED"
}

# ---------------------------
# Validate IAM Revocation
# ---------------------------
iam_revocation_verified if {
    input.user_account_disabled == true
    input.privileged_group_memberships_removed == true
    input.access_revocation_timestamp != ""
}

# ---------------------------
# Validate Session Revocation
# ---------------------------
session_revocation_verified if {
    input.active_sessions_revoked == true
    input.session_revocation_timestamp != ""
}

# ---------------------------
# Validate Revocation Timeliness
# ---------------------------
revocation_timeliness_verified if {
    input.wipe_action_timestamp != ""
    input.access_revocation_timestamp != ""
    input.revocation_timeline_compliant == true
}

# ---------------------------
# Validate Audit Traceability
# ---------------------------
audit_traceability_verified if {
    input.audit_logs_available == true
    input.wipe_event_traceable == true
    input.account_revocation_traceable == true
    input.group_removal_traceable == true
    input.session_revocation_traceable == true
    input.operator_identity_available == true
    input.audit_event_timestamps_available == true
}

# ---------------------------
# Validate Procedure Review
# ---------------------------
procedure_review_verified if {
    input.runbook_periodic_review_enabled == true
    input.runbook_last_review_date != ""
    input.runbook_review_owner != ""
}

# ---------------------------
# Supporting Control:
# IAM Deprovisioning
# ---------------------------
iam_deprovisioning_verified if {
    input.iam_deprovisioning_workflow_defined == true
    input.account_disable_automation_enabled == true
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    wipe_policies := get_array(input, "wipe_policies")
    wipe_events := get_array(input, "wipe_events")
    revocation_events := get_array(input, "revocation_events")
    affected_devices := get_array(input, "affected_devices")
    audit_events := get_array(input, "audit_events")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": affected_devices,

        "details": {
            "remote_wipe_policy_defined":
                input.remote_wipe_policy_defined,

            "remote_wipe_conditions_defined":
                input.remote_wipe_conditions_defined,

            "remote_wipe_authority_defined":
                input.remote_wipe_authority_defined,

            "portable_device_scope_defined":
                input.portable_device_scope_defined,

            "enterprise_owned_devices_defined":
                input.enterprise_owned_devices_defined,

            "portable_device_fleet_count":
                input.portable_device_fleet_count,

            "remote_wipe_capability_enabled":
                input.remote_wipe_capability_enabled,

            "corporate_wipe_capability_enabled":
                input.corporate_wipe_capability_enabled,

            "wipe_policy_assignment_defined":
                input.wipe_policy_assignment_defined,

            "wipe_policy_assignment_scope_defined":
                input.wipe_policy_assignment_scope_defined,

            "in_scope_devices_enrolled":
                input.in_scope_devices_enrolled,

            "lost_device_runbook_available":
                input.lost_device_runbook_available,

            "offboarding_runbook_available":
                input.offboarding_runbook_available,

            "runbook_roles_defined":
                input.runbook_roles_defined,

            "runbook_approval_date":
                input.runbook_approval_date,

            "runbook_last_review_date":
                input.runbook_last_review_date,

            "wipe_timeline_defined":
                input.wipe_timeline_defined,

            "access_revocation_timeline_defined":
                input.access_revocation_timeline_defined,

            "wipe_test_performed":
                input.wipe_test_performed,

            "wipe_test_device":
                input.wipe_test_device,

            "wipe_action_timestamp":
                input.wipe_action_timestamp,

            "wipe_action_outcome":
                input.wipe_action_outcome,

            "user_account_disabled":
                input.user_account_disabled,

            "privileged_group_memberships_removed":
                input.privileged_group_memberships_removed,

            "access_revocation_timestamp":
                input.access_revocation_timestamp,

            "active_sessions_revoked":
                input.active_sessions_revoked,

            "session_revocation_timestamp":
                input.session_revocation_timestamp,

            "revocation_timeline_compliant":
                input.revocation_timeline_compliant,

            "audit_logs_available":
                input.audit_logs_available,

            "wipe_event_traceable":
                input.wipe_event_traceable,

            "account_revocation_traceable":
                input.account_revocation_traceable,

            "group_removal_traceable":
                input.group_removal_traceable,

            "session_revocation_traceable":
                input.session_revocation_traceable,

            "operator_identity_available":
                input.operator_identity_available,

            "audit_event_timestamps_available":
                input.audit_event_timestamps_available,

            "runbook_periodic_review_enabled":
                input.runbook_periodic_review_enabled,

            "runbook_review_owner":
                input.runbook_review_owner,

            "iam_deprovisioning_workflow_defined":
                input.iam_deprovisioning_workflow_defined,

            "account_disable_automation_enabled":
                input.account_disable_automation_enabled,

            "wipe_policy_count":
                count(wipe_policies),

            "wipe_event_count":
                count(wipe_events),

            "revocation_event_count":
                count(revocation_events),

            "affected_device_count":
                count(affected_devices),

            "audit_event_count":
                count(audit_events),

            "requires_sample_evidence":
                true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------

generate_message := msg if {
    not remote_wipe_process_defined
    msg := "FAIL: Remote wipe policy, triggering conditions, or authorization process is not defined"
}

generate_message := msg if {
    remote_wipe_process_defined
    not portable_device_scope_defined
    msg := "INCONCLUSIVE: Enterprise-owned portable device scope cannot be verified"
}

generate_message := msg if {
    portable_device_scope_defined
    not remote_wipe_capability_verified
    msg := "FAIL: Remote wipe or corporate wipe capability is not enabled"
}

generate_message := msg if {
    remote_wipe_capability_verified
    not wipe_assignment_verified
    msg := "FAIL: Remote wipe policy is not assigned to the in-scope portable device fleet"
}

generate_message := msg if {
    wipe_assignment_verified
    not lost_device_runbook_verified
    msg := "FAIL: Lost-device and offboarding procedures, responsibilities, or response timelines are not adequately documented"
}

generate_message := msg if {
    lost_device_runbook_verified
    not wipe_execution_verified
    msg := "INCONCLUSIVE: Remote wipe capability is configured but a completed wipe event cannot be demonstrated"
}

generate_message := msg if {
    wipe_execution_verified
    not iam_revocation_verified
    msg := "FAIL: User account or privileged access was not revoked following the wipe event"
}

generate_message := msg if {
    iam_revocation_verified
    not session_revocation_verified
    msg := "FAIL: Active sessions were not revoked following the device wipe event"
}

generate_message := msg if {
    session_revocation_verified
    not revocation_timeliness_verified
    msg := "FAIL: Access revocation was not completed within the organization's defined response timeline"
}

generate_message := msg if {
    revocation_timeliness_verified
    not audit_traceability_verified
    msg := "INCONCLUSIVE: Wipe and access revocation actions cannot be fully traced through audit logs"
}

generate_message := msg if {
    audit_traceability_verified
    not procedure_review_verified
    msg := "FAIL: Remote wipe and offboarding procedures are not periodically reviewed"
}

generate_message := msg if {
    procedure_review_verified
    compliant
    msg := "PASS: Remote wipe capability is enabled for portable devices, wipe execution is evidenced, access is revoked in a timely manner, and the process is documented and periodically reviewed"
}

# ---------------------------
# Helper Functions
# ---------------------------

get_array(obj, key) := value if {
    value := obj[key]
} else := []
