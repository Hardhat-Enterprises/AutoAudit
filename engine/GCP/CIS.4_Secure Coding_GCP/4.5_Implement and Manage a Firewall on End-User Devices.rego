# METADATA
# title: Implement and Manage a Firewall on End-User Devices (GCP)
# description: |
#   End-user devices must have a host-based firewall or port-filtering
#   mechanism configured and managed to restrict network traffic.
#
#   The firewall must implement a default-deny posture that drops all
#   traffic except services and ports that have been explicitly allowed.
#
#   The safeguard applies primarily to laptops, desktops, mobile devices,
#   and other supported end-user devices. Endpoint firewall enforcement
#   and compliance reporting are the primary evidence sources.
#
#   Google Cloud implementation uses:
#   - Endpoint management platform policies for host firewall enforcement
#   - Device compliance reporting to demonstrate enforcement coverage
#   - Context-Aware Access as a supporting control for cloud administration
#   - Cloud Logging for denied access event monitoring
#
#   Context-Aware Access does not replace endpoint firewall enforcement.
#   It can be used to restrict access to sensitive Google Cloud resources
#   to managed and compliant devices.
#
#   The control verifies:
#   - An endpoint firewall policy is defined
#   - Default-deny firewall posture is configured
#   - Explicitly allowed services and ports are defined
#   - Firewall policy assignments cover the applicable device groups
#   - Firewall enforcement status is demonstrated through compliance reports
#   - Non-compliant devices can be identified
#   - Exceptions have documented justification and expiry
#   - The endpoint management tool of record is identified
#   - Context-Aware Access is treated as supporting evidence only
#
# related_resources:
# - ref: https://cloud.google.com/access-context-manager/docs/overview
#   description: Context-Aware Access Documentation
# - ref: https://cloud.google.com/access-context-manager/docs/quickstart
#   description: Access Context Manager Documentation
# - ref: https://cloud.google.com/logging/docs
#   description: Cloud Logging Documentation
#
# custom:
#   control_id: CIS-4.5
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.5
#   severity: high
#   service: Endpoint Management / Context-Aware Access
#   asset_type: Devices
#   implementation_group: 1
#   requires_permissions:
#   - logging.viewer
#   - logging.logEntries.list
#   - accesscontextmanager.accessPolicies.get
#   - accesscontextmanager.accessLevels.get

package cis.gcp_foundations.v2_0_0.control_4_5

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient end-user device firewall evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.endpoint_firewall_process_defined == true
    input.endpoint_firewall_scope_defined == true
    endpoint_firewall_policy_verified
    default_deny_posture_verified
    firewall_assignment_verified
    compliance_reporting_verified
    exception_process_verified
    tool_of_record_verified
}

# ---------------------------
# Validate Endpoint Firewall Scope
# ---------------------------
endpoint_firewall_scope_defined if {
    input.endpoint_firewall_scope != ""
    input.device_groups_defined == true
    input.end_user_devices_in_scope == true
}

# ---------------------------
# Validate Endpoint Firewall Policy
# ---------------------------
endpoint_firewall_policy_verified if {
    input.endpoint_firewall_policy_defined == true
    input.firewall_policy_settings_available == true
    input.allowed_services_ports_defined == true
}

# ---------------------------
# Validate Default-Deny Posture
# ---------------------------
default_deny_posture_verified if {
    input.default_deny_enabled == true
    input.implicitly_allowed_traffic_dropped == true
    input.explicit_allow_rules_defined == true
}

# ---------------------------
# Validate Firewall Assignment
# ---------------------------
firewall_assignment_verified if {
    input.firewall_policy_assignment_enabled == true
    input.assignment_device_groups != ""
    input.assignment_scope_verified == true
}

# ---------------------------
# Validate Compliance Reporting
# ---------------------------
compliance_reporting_verified if {
    input.device_firewall_compliance_reporting_available == true
    input.firewall_enabled_status_reported == true
    input.enforcement_coverage_available == true
    input.non_compliant_devices_identified == true
    input.compliance_report_timestamp != ""
}

# ---------------------------
# Validate Exception Process
# ---------------------------
exception_process_verified if {
    every exception in input.firewall_exceptions {
        exception.device_or_group != ""
        exception.business_justification != ""
        exception.approver != ""
        exception.expiry_date != ""
    }
}

exception_process_verified if {
    count(get_array(input, "firewall_exceptions")) == 0
}

# ---------------------------
# Validate Endpoint Management Tool of Record
# ---------------------------
tool_of_record_verified if {
    input.endpoint_management_tool != ""
    input.endpoint_management_tool_of_record_confirmed == true
}

# ---------------------------
# Validate Supporting GCP Controls
# ---------------------------
gcp_supporting_control_verified if {
    input.context_aware_access_in_scope == false
}

gcp_supporting_control_verified if {
    input.context_aware_access_in_scope == true
    input.context_aware_access_rule_configured == true
    input.compliant_device_condition_required == true
    input.protected_applications != ""
}

# ---------------------------
# Validate Denied Access Evidence
# ---------------------------
denied_access_monitoring_verified if {
    input.denied_access_event_available == true
    input.denied_access_event_timestamp != ""
    input.denied_access_event_user != ""
    input.denied_access_event_reason != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    firewall_policies := get_array(input, "endpoint_firewall_policies")
    devices := get_array(input, "affected_devices")
    non_compliant := get_array(input, "non_compliant_devices")
    exceptions := get_array(input, "firewall_exceptions")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": devices,
        "details": {
            "endpoint_firewall_process_defined": input.endpoint_firewall_process_defined,
            "endpoint_firewall_scope": input.endpoint_firewall_scope,
            "endpoint_firewall_policy_defined": input.endpoint_firewall_policy_defined,
            "firewall_policy_settings_available": input.firewall_policy_settings_available,
            "default_deny_enabled": input.default_deny_enabled,
            "implicitly_allowed_traffic_dropped": input.implicitly_allowed_traffic_dropped,
            "explicit_allow_rules_defined": input.explicit_allow_rules_defined,
            "allowed_services_ports_defined": input.allowed_services_ports_defined,
            "firewall_policy_assignment_enabled": input.firewall_policy_assignment_enabled,
            "assignment_device_groups": input.assignment_device_groups,
            "assignment_scope_verified": input.assignment_scope_verified,
            "device_firewall_compliance_reporting_available": input.device_firewall_compliance_reporting_available,
            "firewall_enabled_status_reported": input.firewall_enabled_status_reported,
            "enforcement_coverage_available": input.enforcement_coverage_available,
            "non_compliant_device_count": count(non_compliant),
            "exception_count": count(exceptions),
            "endpoint_management_tool": input.endpoint_management_tool,
            "endpoint_management_tool_of_record_confirmed": input.endpoint_management_tool_of_record_confirmed,
            "context_aware_access_in_scope": input.context_aware_access_in_scope,
            "context_aware_access_rule_configured": input.context_aware_access_rule_configured,
            "compliant_device_condition_required": input.compliant_device_condition_required,
            "protected_applications": input.protected_applications,
            "denied_access_event_available": input.denied_access_event_available,
            "firewall_policy_count": count(firewall_policies),
            "affected_device_count": count(devices),
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.endpoint_firewall_process_defined
    msg := "FAIL: End-user device firewall process is not defined"
}

generate_message := msg if {
    input.endpoint_firewall_process_defined
    not input.endpoint_firewall_scope_defined
    msg := "FAIL: End-user device firewall scope is not defined"
}

generate_message := msg if {
    input.endpoint_firewall_scope_defined
    not endpoint_firewall_policy_verified
    msg := "FAIL: Endpoint firewall policy or explicitly allowed services and ports are not sufficiently defined"
}

generate_message := msg if {
    endpoint_firewall_policy_verified
    not default_deny_posture_verified
    msg := "FAIL: Endpoint firewall does not implement a default-deny posture"
}

generate_message := msg if {
    default_deny_posture_verified
    not firewall_assignment_verified
    msg := "INCONCLUSIVE: Endpoint firewall policy exists but assignment scope cannot be verified"
}

generate_message := msg if {
    firewall_assignment_verified
    not compliance_reporting_verified
    msg := "INCONCLUSIVE: Endpoint firewall assignments exist but compliance and enforcement coverage evidence is missing"
}

generate_message := msg if {
    compliance_reporting_verified
    not exception_process_verified
    msg := "FAIL: Endpoint firewall exceptions are missing justification, approval, or expiry information"
}

generate_message := msg if {
    exception_process_verified
    not tool_of_record_verified
    msg := "INCONCLUSIVE: The endpoint management tool of record cannot be established"
}

generate_message := msg if {
    tool_of_record_verified
    input.context_aware_access_in_scope == true
    not gcp_supporting_control_verified
    msg := "INCONCLUSIVE: Supporting Context-Aware Access configuration cannot be verified"
}

generate_message := msg if {
    tool_of_record_verified
    input.context_aware_access_in_scope == true
    input.context_aware_access_rule_configured == true
    input.compliant_device_condition_required == true
    not denied_access_monitoring_verified
    msg := "INCONCLUSIVE: Context-Aware Access is configured but denied access event evidence is missing"
}

generate_message := msg if {
    tool_of_record_verified
    compliant
    msg := "PASS: End-user device firewalls enforce a default-deny baseline, coverage is evidenced through compliance reporting, and exceptions are controlled"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
