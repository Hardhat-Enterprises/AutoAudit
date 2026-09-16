# METADATA
# title: Address Unauthorized Software (GCP)
# description: |
#   Unauthorized software must be identified and either removed from enterprise
#   assets or documented with an approved, time-bound exception. Reviews must
#   occur at least monthly.
#
#   Google Cloud implementation uses:
#   - OS Config / VM Manager OS Inventory to identify unauthorized software
#   - OS Config OS Policies or automation to remove or disable software
#   - Binary Authorization to prevent deployment of unauthorized container images
#   - Cloud Logging and Security Command Center for policy violations
#   - Monthly review workflow using BigQuery, scheduled exports, or a CMDB
#
#   The control verifies:
#   - Authorized software baseline exists
#   - Unauthorized software detection is performed
#   - Response actions are documented
#   - Exceptions are approved and time-bound
#   - Monthly review schedule exists
#   - Monthly review execution is verified
#
# related_resources:
# - ref: https://cloud.google.com/compute/vm-manager/docs
#   description: VM Manager Documentation
# - ref: https://cloud.google.com/compute/vm-manager/docs/os-policies
#   description: OS Policy Assignments
# - ref: https://cloud.google.com/binary-authorization/docs
#   description: Binary Authorization Documentation
# - ref: https://cloud.google.com/security-command-center/docs
#   description: Security Command Center Documentation
#
# custom:
#   control_id: CIS-2.3
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 2.3
#   severity: high
#   service: VM Manager
#   asset_type: Software
#   implementation_group: 1
#   requires_permissions:
#   - osconfig.inventoryViewer
#   - osconfig.osPolicyAssignments.list
#   - binaryauthorization.policy.get
#   - securitycenter.findings.list

package cis.gcp_foundations.v2_0_0.control_2_3

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient unauthorized software management evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.authorized_software_baseline_defined == true
    unauthorized_detection_verified
    response_actions_verified
    exception_process_verified
    input.review_schedule_defined == true
    review_execution_verified
}

# ---------------------------
# Validate Unauthorized Software Detection
# ---------------------------
unauthorized_detection_verified if {
    detections := get_array(input, "unauthorized_software")

    count(detections) > 0

    every software in detections {
        software.title != ""
        software.asset_id != ""
        software.detected_timestamp != ""
    }
}

unauthorized_detection_verified if {
    count(get_array(input, "unauthorized_software")) == 0
}

# ---------------------------
# Validate Response Actions
# ---------------------------
response_actions_verified if {
    every action in input.response_actions {
        action.software_title != ""
        action.asset_id != ""
        action.action_type != ""
        action.status == "COMPLETED"
        action.timestamp != ""
    }
}

# ---------------------------
# Validate Exception Process
# ---------------------------
exception_process_verified if {
    every exception in input.exception_register {
        exception.software_title != ""
        exception.business_justification != ""
        exception.approver != ""
        exception.expiry_date != ""
    }
}

exception_process_verified if {
    count(get_array(input, "exception_register")) == 0
}

# ---------------------------
# Validate Review Evidence
# ---------------------------
review_execution_verified if {
    input.review_frequency_days <= 31
    input.last_review_timestamp != ""
    input.scheduler_last_run_status == "SUCCESS"
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    detections := get_array(input, "unauthorized_software")
    actions := get_array(input, "response_actions")
    exceptions := get_array(input, "exception_register")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": detections,
        "details": {
            "authorized_software_baseline_defined": input.authorized_software_baseline_defined,
            "unauthorized_software_count": count(detections),
            "response_action_count": count(actions),
            "exception_count": count(exceptions),
            "review_frequency_days": input.review_frequency_days,
            "last_review_timestamp": input.last_review_timestamp,
            "scheduler_last_run_status": input.scheduler_last_run_status,
            "binary_authorization_enabled": input.binary_authorization_enabled,
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.authorized_software_baseline_defined
    msg := "FAIL: Authorized software baseline is not defined"
}

generate_message := msg if {
    input.authorized_software_baseline_defined
    not unauthorized_detection_verified
    msg := "FAIL: No evidence of unauthorized software detection"
}

generate_message := msg if {
    unauthorized_detection_verified
    not response_actions_verified
    msg := "FAIL: Unauthorized software has not been removed, blocked, or otherwise remediated"
}

generate_message := msg if {
    response_actions_verified
    not exception_process_verified
    msg := "FAIL: Unauthorized software exceptions are missing or incomplete"
}

generate_message := msg if {
    exception_process_verified
    not input.review_schedule_defined
    msg := "FAIL: No evidence of a monthly unauthorized software review schedule"
}

generate_message := msg if {
    input.review_schedule_defined
    not review_execution_verified
    msg := "INCONCLUSIVE: Monthly review schedule exists but execution evidence is missing"
}

generate_message := msg if {
    compliant
    msg := "PASS: Unauthorized software is detected, remediated or documented through approved exceptions, and reviewed monthly"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
