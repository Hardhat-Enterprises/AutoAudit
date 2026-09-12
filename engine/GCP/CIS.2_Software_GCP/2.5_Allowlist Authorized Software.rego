# METADATA
# title: Allowlist Authorized Software (GCP)
# description: |
#   Technical controls must enforce that only authorized software can execute
#   or be accessed on enterprise assets. Allowlist rules must be reviewed at
#   least bi-annually or more frequently.
#
#   Google Cloud implementation uses:
#   - Binary Authorization for GKE to enforce approved container images
#   - Artifact Registry to maintain trusted image repositories
#   - Attestors and approval workflows for image authorization
#   - OS Config / VM Manager OS Policies for VM software restrictions
#   - Bi-annual allowlist review process for policies, exceptions, and overrides
#
#   The control verifies:
#   - Allowlisting controls are implemented
#   - Enforcement scope is defined
#   - Enforcement mode is enabled
#   - Approved software/image validation exists
#   - Unauthorized execution attempts are blocked or detected
#   - Allowlist rules and exceptions are reviewed periodically
#
# related_resources:
# - ref: https://cloud.google.com/binary-authorization/docs
#   description: Binary Authorization Documentation
# - ref: https://cloud.google.com/artifact-registry/docs
#   description: Artifact Registry Documentation
# - ref: https://cloud.google.com/compute/vm-manager/docs/os-policies
#   description: VM Manager OS Policies Documentation
#
# custom:
#   control_id: CIS-2.5
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 2.5
#   severity: high
#   service: Binary Authorization
#   asset_type: Software
#   implementation_group: 2
#   requires_permissions:
#   - binaryauthorization.policy.get
#   - binaryauthorization.attestors.list
#   - artifactregistry.repositories.list
#   - osconfig.osPolicyAssignments.list

package cis.gcp_foundations.v2_0_0.control_2_5

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient software allowlisting evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.allowlist_control_enabled == true
    input.allowlist_scope_defined == true
    enforcement_verified
    approval_process_verified
    blocked_execution_verified
    review_execution_verified
}

# ---------------------------
# Validate Enforcement Configuration
# ---------------------------
enforcement_verified if {
    input.binary_authorization_enabled == true
    input.binary_authorization_mode == "ENFORCE"
    input.enforcement_scope != ""
}

enforcement_verified if {
    input.vm_os_policy_enabled == true
    input.os_policy_enforcement_mode == "ENFORCE"
    input.os_policy_scope != ""
}

# ---------------------------
# Validate Approval Process
# ---------------------------
approval_process_verified if {
    every attestor in input.attestors {
        attestor.name != ""
        attestor.status == "ACTIVE"
    }
}

approval_process_verified if {
    count(get_array(input, "attestors")) == 0
    input.vm_os_policy_enabled == true
}

# ---------------------------
# Validate Blocked Execution Evidence
# ---------------------------
blocked_execution_verified if {
    events := get_array(input, "blocked_events")

    count(events) > 0

    every event in events {
        event.software_or_image != ""
        event.timestamp != ""
        event.action == "DENIED"
    }
}

# ---------------------------
# Validate Review Evidence
# ---------------------------
review_execution_verified if {
    input.review_frequency_days <= 183
    input.last_review_timestamp != ""
    input.scheduler_last_run_status == "SUCCESS"
}

# ---------------------------
# Validate Exception Handling
# ---------------------------
exceptions_verified if {
    every exception in input.exceptions {
        exception.software_or_image != ""
        exception.approver != ""
        exception.expiry_date != ""
        exception.business_justification != ""
    }
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    blocked := get_array(input, "blocked_events")
    attestors := get_array(input, "attestors")
    exceptions := get_array(input, "exceptions")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": blocked,
        "details": {
            "allowlist_control_enabled": input.allowlist_control_enabled,
            "allowlist_scope": input.allowlist_scope,
            "binary_authorization_enabled": input.binary_authorization_enabled,
            "binary_authorization_mode": input.binary_authorization_mode,
            "enforcement_scope": input.enforcement_scope,
            "attestor_count": count(attestors),
            "blocked_event_count": count(blocked),
            "exception_count": count(exceptions),
            "review_frequency_days": input.review_frequency_days,
            "last_review_timestamp": input.last_review_timestamp,
            "scheduler_last_run_status": input.scheduler_last_run_status,
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.allowlist_control_enabled
    msg := "FAIL: Software allowlisting controls are not enabled"
}

generate_message := msg if {
    input.allowlist_control_enabled
    not input.allowlist_scope_defined
    msg := "FAIL: Allowlist enforcement scope is not defined"
}

generate_message := msg if {
    input.allowlist_scope_defined
    not enforcement_verified
    msg := "FAIL: Allowlist enforcement is not enabled for the defined scope"
}

generate_message := msg if {
    enforcement_verified
    not approval_process_verified
    msg := "FAIL: Software/image approval process is not configured"
}

generate_message := msg if {
    approval_process_verified
    not blocked_execution_verified
    msg := "FAIL: No evidence of blocked unauthorized software execution or deployment attempts"
}

generate_message := msg if {
    blocked_execution_verified
    not review_execution_verified
    msg := "INCONCLUSIVE: Allowlist enforcement exists but bi-annual review evidence is missing"
}

generate_message := msg if {
    review_execution_verified
    compliant
    msg := "PASS: Authorized software allowlisting is enforced, unauthorized execution is blocked, and rules are reviewed bi-annually"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
