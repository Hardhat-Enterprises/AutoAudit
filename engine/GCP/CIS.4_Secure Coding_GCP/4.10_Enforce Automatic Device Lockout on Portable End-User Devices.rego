# METADATA
# title: Enforce Automatic Device Lockout on Portable End-User Devices (GCP)
# description: |
#   Portable end-user devices must enforce automatic device lockout after
#   a predetermined number of consecutive local authentication failures.
#
#   CIS thresholds:
#   - Laptops: no more than 20 failed authentication attempts
#   - Tablets and smartphones: no more than 10 failed authentication attempts
#
#   The primary enforcement mechanism is the organization's endpoint
#   management platform. Google Cloud controls do not directly implement
#   local failed-authentication thresholds on laptops, tablets, or
#   smartphones.
#
#   Google Cloud Context-Aware Access may provide supporting protection
#   for sensitive cloud resources by requiring managed and compliant
#   devices. It may also provide evidence of denied access resulting from
#   device posture failures. However, Context-Aware Access does not replace
#   the local device lockout control.
#
#   The control verifies:
#   - Portable device lockout policy is defined
#   - Laptop lockout threshold is no greater than 20 attempts
#   - Tablet and smartphone lockout threshold is no greater than 10 attempts
#   - Policy is assigned to the portable device fleet
#   - Compliance reporting demonstrates coverage
#   - Non-compliant devices are identified
#   - Exceptions are documented and time-bound
#   - Lockout enforcement has been tested or operationally evidenced
#   - GCP Context-Aware Access is treated only as a supporting control
#
# related_resources:
# - ref: https://cloud.google.com/access-context-manager/docs/overview
#   description: Google Cloud Access Context Manager Documentation
# - ref: https://cloud.google.com/access-context-manager/docs/device-policy
#   description: Access Context Manager Device Policy Documentation
#
# custom:
#   control_id: CIS-4.10
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.10
#   severity: medium
#   service: Endpoint Management / Context-Aware Access
#   asset_type: Devices
#   implementation_group: 2
#   requires_permissions:
#   - accesscontextmanager.accessPolicies.get
#   - accesscontextmanager.policies.get
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_4_10

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient portable device lockout evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    lockout_process_defined
    portable_device_scope_defined
    laptop_lockout_verified
    mobile_lockout_verified
    policy_assignment_verified
    compliance_reporting_verified
    exception_management_verified
    enforcement_evidence_verified
}

# ---------------------------
# Validate Lockout Process
# ---------------------------
lockout_process_defined if {
    input.device_lockout_policy_defined == true
    input.local_authentication_lockout_enabled == true
    input.lockout_threshold_standard_defined == true
}

# ---------------------------
# Validate Portable Device Scope
# ---------------------------
portable_device_scope_defined if {
    input.portable_device_scope_defined == true
    input.laptop_scope_defined == true
    input.tablet_scope_defined == true
    input.smartphone_scope_defined == true
    input.portable_device_fleet_count > 0
}

# ---------------------------
# Validate Laptop Threshold
# CIS requirement: <= 20 attempts
# ---------------------------
laptop_lockout_verified if {
    input.laptop_lockout_threshold > 0
    input.laptop_lockout_threshold <= 20
}

# ---------------------------
# Validate Tablet Threshold
# CIS requirement: <= 10 attempts
# ---------------------------
tablet_lockout_verified if {
    input.tablet_lockout_threshold > 0
    input.tablet_lockout_threshold <= 10
}

# ---------------------------
# Validate Smartphone Threshold
# CIS requirement: <= 10 attempts
# ---------------------------
smartphone_lockout_verified if {
    input.smartphone_lockout_threshold > 0
    input.smartphone_lockout_threshold <= 10
}

# ---------------------------
# Validate Mobile Device Policy
# Both tablet and smartphone thresholds
# must satisfy the CIS requirement.
# ---------------------------
mobile_lockout_verified if {
    tablet_lockout_verified
    smartphone_lockout_verified
}

# ---------------------------
# Validate Policy Assignment
# ---------------------------
policy_assignment_verified if {
    input.lockout_policy_assignment_defined == true
    input.lockout_policy_assignment_scope_defined == true
    input.portable_devices_targeted == true
}

# ---------------------------
# Validate Compliance Reporting
# ---------------------------
compliance_reporting_verified if {
    input.device_compliance_report_available == true
    input.fleet_coverage_reported == true
    input.non_compliant_devices_identified == true
    input.compliance_report_timestamp != ""
}

# ---------------------------
# Validate Fleet Coverage
# ---------------------------
coverage_verified if {
    input.portable_device_fleet_count > 0
    input.compliant_device_count >= 0
    input.non_compliant_device_count >= 0

    input.portable_device_fleet_count ==
        input.compliant_device_count +
        input.non_compliant_device_count
}

# ---------------------------
# Validate Exception Management
# ---------------------------
exception_management_verified if {
    input.exception_process_defined == true

    every exception in input.lockout_exceptions {
        exception.device != ""
        exception.device_type != ""
        exception.business_justification != ""
        exception.approver != ""
        exception.expiry_date != ""
    }
}

exception_management_verified if {
    count(get_array(input, "lockout_exceptions")) == 0
}

# ---------------------------
# Validate Lockout Enforcement
# ---------------------------
enforcement_evidence_verified if {
    input.lockout_enforcement_tested == true
    input.lockout_test_device != ""
    input.lockout_event_evidence_available == true
}

# ---------------------------
# Supporting GCP Control
# Context-Aware Access does NOT replace
# local device lockout.
# ---------------------------
context_aware_access_verified if {
    input.context_aware_access_in_scope == false
}

context_aware_access_verified if {
    input.context_aware_access_in_scope == true
    input.context_aware_access_policy_defined == true
    input.managed_device_required == true
    input.compliant_device_required == true
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    lockout_policies := get_array(input, "lockout_policies")
    non_compliant_devices := get_array(input, "non_compliant_devices")
    exceptions := get_array(input, "lockout_exceptions")
    lockout_events := get_array(input, "lockout_events")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": non_compliant_devices,

        "details": {
            "device_lockout_policy_defined":
                input.device_lockout_policy_defined,

            "local_authentication_lockout_enabled":
                input.local_authentication_lockout_enabled,

            "lockout_threshold_standard_defined":
                input.lockout_threshold_standard_defined,

            "portable_device_scope_defined":
                input.portable_device_scope_defined,

            "laptop_scope_defined":
                input.laptop_scope_defined,

            "tablet_scope_defined":
                input.tablet_scope_defined,

            "smartphone_scope_defined":
                input.smartphone_scope_defined,

            "portable_device_fleet_count":
                input.portable_device_fleet_count,

            "laptop_lockout_threshold":
                input.laptop_lockout_threshold,

            "tablet_lockout_threshold":
                input.tablet_lockout_threshold,

            "smartphone_lockout_threshold":
                input.smartphone_lockout_threshold,

            "laptop_threshold_requirement":
                "20 attempts or fewer",

            "tablet_threshold_requirement":
                "10 attempts or fewer",

            "smartphone_threshold_requirement":
                "10 attempts or fewer",

            "lockout_policy_assignment_defined":
                input.lockout_policy_assignment_defined,

            "lockout_policy_assignment_scope_defined":
                input.lockout_policy_assignment_scope_defined,

            "portable_devices_targeted":
                input.portable_devices_targeted,

            "device_compliance_report_available":
                input.device_compliance_report_available,

            "fleet_coverage_reported":
                input.fleet_coverage_reported,

            "non_compliant_devices_identified":
                input.non_compliant_devices_identified,

            "compliance_report_timestamp":
                input.compliance_report_timestamp,

            "compliant_device_count":
                input.compliant_device_count,

            "non_compliant_device_count":
                input.non_compliant_device_count,

            "lockout_enforcement_tested":
                input.lockout_enforcement_tested,

            "lockout_test_device":
                input.lockout_test_device,

            "lockout_event_evidence_available":
                input.lockout_event_evidence_available,

            "context_aware_access_in_scope":
                input.context_aware_access_in_scope,

            "context_aware_access_policy_defined":
                input.context_aware_access_policy_defined,

            "managed_device_required":
                input.managed_device_required,

            "compliant_device_required":
                input.compliant_device_required,

            "exception_count":
                count(exceptions),

            "lockout_policy_count":
                count(lockout_policies),

            "non_compliant_device_count":
                count(non_compliant_devices),

            "lockout_event_count":
                count(lockout_events),

            "requires_sample_evidence":
                true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------

generate_message := msg if {
    not lockout_process_defined
    msg := "FAIL: Local device lockout policy or authentication lockout standard is not defined"
}

generate_message := msg if {
    lockout_process_defined
    not portable_device_scope_defined
    msg := "INCONCLUSIVE: Portable device fleet scope cannot be verified"
}

generate_message := msg if {
    portable_device_scope_defined
    not laptop_lockout_verified
    msg := "FAIL: Laptop lockout threshold is greater than 20 attempts or is not configured"
}

generate_message := msg if {
    laptop_lockout_verified
    not tablet_lockout_verified
    msg := "FAIL: Tablet lockout threshold is greater than 10 attempts or is not configured"
}

generate_message := msg if {
    tablet_lockout_verified
    not smartphone_lockout_verified
    msg := "FAIL: Smartphone lockout threshold is greater than 10 attempts or is not configured"
}

generate_message := msg if {
    smartphone_lockout_verified
    not policy_assignment_verified
    msg := "INCONCLUSIVE: Lockout policy assignment and portable-device coverage cannot be verified"
}

generate_message := msg if {
    policy_assignment_verified
    not compliance_reporting_verified
    msg := "INCONCLUSIVE: Device lockout policy exists but fleet compliance reporting is missing"
}

generate_message := msg if {
    compliance_reporting_verified
    not coverage_verified
    msg := "INCONCLUSIVE: Compliance report does not establish complete portable-device fleet coverage"
}

generate_message := msg if {
    coverage_verified
    not exception_management_verified
    msg := "FAIL: Lockout policy exceptions are not controlled with documented justification, approval, and expiry"
}

generate_message := msg if {
    exception_management_verified
    not enforcement_evidence_verified
    msg := "INCONCLUSIVE: Lockout settings are configured but operational enforcement evidence is missing"
}

generate_message := msg if {
    enforcement_evidence_verified
    not context_aware_access_verified
    msg := "INCONCLUSIVE: Supporting Context-Aware Access controls are configured incorrectly or cannot be verified"
}

generate_message := msg if {
    context_aware_access_verified
    compliant
    msg := "PASS: Portable device lockout thresholds meet CIS requirements, policy coverage is demonstrated, exceptions are governed, and operational enforcement is evidenced"
}

# ---------------------------
# Helper Functions
# ---------------------------

get_array(obj, key) := value if {
    value := obj[key]
} else := []
