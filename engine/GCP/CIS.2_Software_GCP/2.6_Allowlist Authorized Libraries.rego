# METADATA
# title: Allowlist Authorized Libraries (GCP)
# description: |
#   Technical controls must ensure that only authorized software libraries,
#   dependencies, and runtime components are permitted to load into system
#   processes. Unauthorized libraries must be blocked from use. Approved
#   library baselines must be reviewed at least bi-annually or more frequently.
#
#   Google Cloud implementation uses:
#   - Binary Authorization for GKE deployment enforcement
#   - Signed image attestations to validate trusted artifacts
#   - SBOM generation and dependency scanning during CI/CD
#   - Artifact Registry for approved container artifacts
#   - OS Config / VM Manager OS Policies for VM package restrictions
#   - File integrity monitoring signals for critical library paths where feasible
#   - Bi-annual approved library baseline review process
#
#   The control verifies:
#   - Approved library policy exists
#   - Library validation is automated
#   - Unauthorized dependencies are blocked
#   - Deployment enforcement is enabled
#   - Exceptions are approved and time-bound
#   - Library allowlist reviews are performed periodically
#
# related_resources:
# - ref: https://cloud.google.com/binary-authorization/docs
#   description: Binary Authorization Documentation
# - ref: https://cloud.google.com/artifact-registry/docs
#   description: Artifact Registry Documentation
# - ref: https://cloud.google.com/compute/vm-manager/docs/os-policies
#   description: VM Manager OS Policies Documentation
# - ref: https://cloud.google.com/software-supply-chain-security/docs
#   description: Software Supply Chain Security Documentation
#
# custom:
#   control_id: CIS-2.6
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 2.6
#   severity: high
#   service: Binary Authorization
#   asset_type: Software
#   implementation_group: 2
#   requires_permissions:
#   - binaryauthorization.policy.get
#   - binaryauthorization.attestors.list
#   - artifactregistry.repositories.list
#   - osconfig.osPolicyAssignments.list

package cis.gcp_foundations.v2_0_0.control_2_6

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient authorized library control evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.library_policy_defined == true
    input.library_scope_defined == true
    dependency_validation_verified
    deployment_enforcement_verified
    exception_process_verified
    review_execution_verified
}

# ---------------------------
# Validate Library Policy
# ---------------------------
dependency_validation_verified if {
    input.sbom_validation_enabled == true
    input.dependency_policy_enabled == true
}

dependency_validation_verified if {
    input.vm_library_controls_enabled == true
    input.os_policy_enforcement_mode == "ENFORCE"
}

# ---------------------------
# Validate Deployment Enforcement
# ---------------------------
deployment_enforcement_verified if {
    input.binary_authorization_enabled == true
    input.binary_authorization_mode == "ENFORCE"
    input.denied_deployment_evidence == true
}

deployment_enforcement_verified if {
    input.cicd_dependency_gate_enabled == true
    input.failed_build_evidence == true
}

# ---------------------------
# Validate Exception Process
# ---------------------------
exception_process_verified if {
    every exception in input.library_exceptions {
        exception.library_name != ""
        exception.business_justification != ""
        exception.approver != ""
        exception.expiry_date != ""
    }
}

exception_process_verified if {
    count(get_array(input, "library_exceptions")) == 0
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
# Validate Approved Library Baseline
# ---------------------------
approved_library_verified if {
    every library in input.approved_libraries {
        library.name != ""
        library.version != ""
        library.source != ""
    }
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    libraries := get_array(input, "approved_libraries")
    exceptions := get_array(input, "library_exceptions")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": libraries,
        "details": {
            "library_policy_defined": input.library_policy_defined,
            "library_scope": input.library_scope,
            "approved_library_count": count(libraries),
            "sbom_validation_enabled": input.sbom_validation_enabled,
            "dependency_policy_enabled": input.dependency_policy_enabled,
            "binary_authorization_enabled": input.binary_authorization_enabled,
            "binary_authorization_mode": input.binary_authorization_mode,
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
    not input.library_policy_defined
    msg := "FAIL: Approved library policy is not defined"
}

generate_message := msg if {
    input.library_policy_defined
    not input.library_scope_defined
    msg := "FAIL: Library control scope is not defined"
}

generate_message := msg if {
    input.library_scope_defined
    not dependency_validation_verified
    msg := "FAIL: Library dependency validation controls are not enabled"
}

generate_message := msg if {
    dependency_validation_verified
    not deployment_enforcement_verified
    msg := "FAIL: Unauthorized libraries are not blocked through build or deployment enforcement"
}

generate_message := msg if {
    deployment_enforcement_verified
    not approved_library_verified
    msg := "FAIL: Approved library baseline is missing or incomplete"
}

generate_message := msg if {
    approved_library_verified
    not exception_process_verified
    msg := "FAIL: Library exceptions are missing required approval or expiry information"
}

generate_message := msg if {
    exception_process_verified
    not review_execution_verified
    msg := "INCONCLUSIVE: Library policy review cadence exists but execution evidence is missing"
}

generate_message := msg if {
    review_execution_verified
    compliant
    msg := "PASS: Authorized libraries are enforced through dependency and deployment controls with bi-annual review evidence"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
