# METADATA
# title: Configure Automatic Session Locking on Enterprise Assets (GCP)
# description: |
#   Enterprise assets must be configured to automatically lock user sessions
#   after a defined period of inactivity.
#
#   For general-purpose operating systems, the inactivity timeout must not
#   exceed 15 minutes. For mobile end-user devices, the inactivity timeout
#   must not exceed 2 minutes.
#
#   Session locking must be enforced at the operating-system or endpoint
#   management level. Cloud console session settings may complement the
#   control but do not replace OS-level session locking.
#
#   Google Cloud implementation uses:
#   - Endpoint/device management platform policies for laptops and desktops
#   - Mobile device management policies for mobile end-user devices
#   - OS Config / VM Manager OS Policies for interactive Compute Engine
#     instances where applicable
#   - Cloud Workstations policies where interactive workstations are in scope
#   - Cloud Identity sign-in controls as a supplementary control for
#     administrative web sessions
#
#   The control verifies:
#   - Automatic session locking is configured
#   - General-purpose operating systems use a timeout of 15 minutes or less
#   - Mobile devices use a timeout of 2 minutes or less
#   - Password-on-resume is enabled
#   - Policy assignments cover the relevant device fleet
#   - Fleet compliance reporting is available
#   - Non-compliant devices can be identified
#   - Exceptions have documented justification and expiry
#   - Interactive GCP endpoints are appropriately scoped
#
# related_resources:
# - ref: https://cloud.google.com/compute/vm-manager/docs/os-policies
#   description: VM Manager OS Policies Documentation
# - ref: https://cloud.google.com/workstations/docs
#   description: Cloud Workstations Documentation
# - ref: https://cloud.google.com/identity/docs
#   description: Cloud Identity Documentation
# - ref: https://cloud.google.com/logging/docs
#   description: Cloud Logging Documentation
#
# custom:
#   control_id: CIS-4.3
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.3
#   severity: high
#   service: Endpoint Management / OS Config
#   asset_type: Devices
#   implementation_group: 1
#   requires_permissions:
#   - osconfig.osPolicyAssignments.list
#   - osconfig.osPolicyCompliances.list
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_4_3

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient automatic session locking evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.session_lock_policy_defined == true
    input.device_scope_defined == true
    session_lock_policy_verified
    session_lock_assignment_verified
    fleet_compliance_verified
    exception_process_verified
    gcp_interactive_scope_verified
}

# ---------------------------
# Validate Session Lock Policy
# ---------------------------
session_lock_policy_verified if {
    input.desktop_timeout_minutes <= 15
    input.mobile_timeout_minutes <= 2
    input.password_on_resume_required == true
}

# ---------------------------
# Validate Device Scope
# ---------------------------
device_scope_defined if {
    input.device_scope != ""
    input.desktop_device_scope_defined == true
    input.mobile_device_scope_defined == true
}

# ---------------------------
# Validate Session Lock Policy Metadata
# ---------------------------
session_lock_policy_document_verified if {
    input.session_lock_policy_title != ""
    input.session_lock_policy_version != ""
    input.session_lock_policy_approval_date != ""
    input.session_lock_policy_review_date != ""
}

# ---------------------------
# Validate Policy Assignment
# ---------------------------
session_lock_assignment_verified if {
    input.policy_assignment_enabled == true
    input.desktop_assignment_targets != ""
    input.mobile_assignment_targets != ""
    input.assignment_scope_verified == true
}

# ---------------------------
# Validate Fleet Compliance
# ---------------------------
fleet_compliance_verified if {
    input.fleet_compliance_reporting_available == true
    input.compliance_summary_available == true
    input.non_compliant_devices_identified == true
    input.compliance_report_timestamp != ""
}

# ---------------------------
# Validate Exception Process
# ---------------------------
exception_process_verified if {
    every exception in input.session_lock_exceptions {
        exception.device_or_group != ""
        exception.business_justification != ""
        exception.approver != ""
        exception.expiry_date != ""
    }
}

exception_process_verified if {
    count(get_array(input, "session_lock_exceptions")) == 0
}

# ---------------------------
# Validate GCP Interactive Endpoint Scope
# ---------------------------
gcp_interactive_scope_verified if {
    input.gcp_interactive_endpoints_in_scope == true
    input.os_config_session_lock_policy_enabled == true
    input.os_config_compliance_available == true
}

gcp_interactive_scope_verified if {
    input.gcp_interactive_endpoints_in_scope == false
    input.primary_evidence_location != ""
    input.primary_evidence_location != "GCP Cloud Console session settings only"
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    exceptions := get_array(input, "session_lock_exceptions")
    devices := get_array(input, "affected_devices")
    non_compliant := get_array(input, "non_compliant_devices")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": devices,
        "details": {
            "session_lock_policy_defined": input.session_lock_policy_defined,
            "device_scope": input.device_scope,
            "desktop_timeout_minutes": input.desktop_timeout_minutes,
            "mobile_timeout_minutes": input.mobile_timeout_minutes,
            "password_on_resume_required": input.password_on_resume_required,
            "session_lock_policy_title": input.session_lock_policy_title,
            "session_lock_policy_version": input.session_lock_policy_version,
            "session_lock_policy_approval_date": input.session_lock_policy_approval_date,
            "session_lock_policy_review_date": input.session_lock_policy_review_date,
            "policy_assignment_enabled": input.policy_assignment_enabled,
            "desktop_assignment_targets": input.desktop_assignment_targets,
            "mobile_assignment_targets": input.mobile_assignment_targets,
            "fleet_compliance_reporting_available": input.fleet_compliance_reporting_available,
            "compliance_summary_available": input.compliance_summary_available,
            "non_compliant_device_count": count(non_compliant),
            "exception_count": count(exceptions),
            "gcp_interactive_endpoints_in_scope": input.gcp_interactive_endpoints_in_scope,
            "os_config_session_lock_policy_enabled": input.os_config_session_lock_policy_enabled,
            "os_config_compliance_available": input.os_config_compliance_available,
            "primary_evidence_location": input.primary_evidence_location,
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.session_lock_policy_defined
    msg := "FAIL: Automatic session locking policy is not defined"
}

generate_message := msg if {
    input.session_lock_policy_defined
    not input.device_scope_defined
    msg := "FAIL: Session locking device scope is not defined"
}

generate_message := msg if {
    input.device_scope_defined
    not session_lock_policy_verified
    msg := "FAIL: Session lock timeout exceeds CIS threshold or password-on-resume is not enforced"
}

generate_message := msg if {
    session_lock_policy_verified
    not session_lock_policy_document_verified
    msg := "FAIL: Session locking policy documentation is missing approval, version, or review evidence"
}

generate_message := msg if {
    session_lock_policy_document_verified
    not session_lock_assignment_verified
    msg := "INCONCLUSIVE: Session locking policy exists but assignment targets or scope cannot be verified"
}

generate_message := msg if {
    session_lock_assignment_verified
    not fleet_compliance_verified
    msg := "INCONCLUSIVE: Session locking assignments exist but fleet compliance evidence is missing"
}

generate_message := msg if {
    fleet_compliance_verified
    not exception_process_verified
    msg := "FAIL: Session locking exceptions are missing justification, approval, or expiry information"
}

generate_message := msg if {
    exception_process_verified
    not gcp_interactive_scope_verified
    msg := "INCONCLUSIVE: GCP interactive endpoint scope or OS-level session locking evidence is missing"
}

generate_message := msg if {
    input.gcp_interactive_endpoints_in_scope == true
    input.os_config_session_lock_policy_enabled == false
    msg := "FAIL: GCP interactive endpoints are in scope but OS-level session locking is not enforced"
}

generate_message := msg if {
    input.gcp_interactive_endpoints_in_scope == true
    input.os_config_session_lock_policy_enabled == true
    input.os_config_compliance_available == false
    msg := "INCONCLUSIVE: OS Config session locking is configured but compliance evidence is missing"
}

generate_message := msg if {
    gcp_interactive_scope_verified
    compliant
    msg := "PASS: Automatic session locking is enforced within CIS-aligned timeouts, fleet coverage is evidenced, and exceptions are controlled"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
