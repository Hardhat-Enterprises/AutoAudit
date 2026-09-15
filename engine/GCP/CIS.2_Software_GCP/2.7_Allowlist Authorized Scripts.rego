# METADATA
# title: Allowlist Authorized Scripts (GCP)
# description: |
#   Technical controls must ensure that only authorized scripts are permitted
#   to execute within enterprise environments. Script execution must be
#   controlled through approved sources, digital signatures, version control,
#   or equivalent enforcement mechanisms. Unauthorized scripts must be blocked.
#   Script allowlist rules and exceptions must be reviewed at least bi-annually.
#
#   Google Cloud implementation uses:
#   - Cloud Build or CI/CD pipelines for controlled script development and release
#   - Artifact Registry for approved script artefacts and deployment packages
#   - Binary Authorization for trusted container image deployment
#   - Source control repositories for approved script ownership and versioning
#   - OS Config / VM Manager OS Policies for VM script execution controls
#   - Cloud Logging and alerting for unauthorized script execution attempts
#
#   The control verifies:
#   - Authorized script sources are defined
#   - Script execution controls are enforced
#   - Unauthorized scripts are blocked or detected
#   - Monitoring and alerting exists
#   - Exceptions are approved and time-bound
#   - Script allowlist rules are reviewed periodically
#
# related_resources:
# - ref: https://cloud.google.com/build/docs
#   description: Cloud Build Documentation
# - ref: https://cloud.google.com/binary-authorization/docs
#   description: Binary Authorization Documentation
# - ref: https://cloud.google.com/artifact-registry/docs
#   description: Artifact Registry Documentation
# - ref: https://cloud.google.com/compute/vm-manager/docs/os-policies
#   description: VM Manager OS Policies Documentation
# - ref: https://cloud.google.com/logging/docs
#   description: Cloud Logging Documentation
#
# custom:
#   control_id: CIS-2.7
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 2.7
#   severity: high
#   service: OS Config
#   asset_type: Software
#   implementation_group: 3
#   requires_permissions:
#   - osconfig.osPolicyAssignments.list
#   - logging.viewer
#   - cloudbuild.builds.list
#   - artifactregistry.repositories.list

package cis.gcp_foundations.v2_0_0.control_2_7

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient authorized script control evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.script_allowlist_defined == true
    input.script_scope_defined == true
    script_source_verified
    execution_control_verified
    unauthorized_execution_monitoring_verified
    exception_process_verified
    review_execution_verified
}

# ---------------------------
# Validate Authorized Script Sources
# ---------------------------
script_source_verified if {
    every script in input.authorized_scripts {
        script.name != ""
        script.source_repository != ""
        script.version != ""
        script.owner != ""
    }
}

# ---------------------------
# Validate Execution Controls
# ---------------------------
execution_control_verified if {
    input.os_policy_enabled == true
    input.os_policy_enforcement_mode == "ENFORCE"
    input.os_policy_scope != ""
}

execution_control_verified if {
    input.cicd_script_control_enabled == true
    input.approved_repository_enforced == true
}

# ---------------------------
# Validate Unauthorized Script Monitoring
# ---------------------------
unauthorized_execution_monitoring_verified if {
    input.logging_enabled == true
    input.alerting_enabled == true
    input.blocked_script_event_available == true
}

# ---------------------------
# Validate Exception Process
# ---------------------------
exception_process_verified if {
    every exception in input.script_exceptions {
        exception.script_name != ""
        exception.business_justification != ""
        exception.approver != ""
        exception.expiry_date != ""
    }
}

exception_process_verified if {
    count(get_array(input, "script_exceptions")) == 0
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
# Result Output
# ---------------------------
result := output if {

    scripts := get_array(input, "authorized_scripts")
    exceptions := get_array(input, "script_exceptions")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": scripts,
        "details": {
            "script_allowlist_defined": input.script_allowlist_defined,
            "script_scope": input.script_scope,
            "authorized_script_count": count(scripts),
            "os_policy_enabled": input.os_policy_enabled,
            "cicd_script_control_enabled": input.cicd_script_control_enabled,
            "logging_enabled": input.logging_enabled,
            "alerting_enabled": input.alerting_enabled,
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
    not input.script_allowlist_defined
    msg := "FAIL: Authorized script allowlist is not defined"
}

generate_message := msg if {
    input.script_allowlist_defined
    not input.script_scope_defined
    msg := "FAIL: Script execution control scope is not defined"
}

generate_message := msg if {
    input.script_scope_defined
    not script_source_verified
    msg := "FAIL: Authorized script sources and ownership are not defined"
}

generate_message := msg if {
    script_source_verified
    not execution_control_verified
    msg := "FAIL: Script execution controls are not enforced"
}

generate_message := msg if {
    execution_control_verified
    not unauthorized_execution_monitoring_verified
    msg := "FAIL: Unauthorized script execution monitoring or alerting is not configured"
}

generate_message := msg if {
    unauthorized_execution_monitoring_verified
    not exception_process_verified
    msg := "FAIL: Script execution exceptions are missing approval or expiry information"
}

generate_message := msg if {
    exception_process_verified
    not review_execution_verified
    msg := "INCONCLUSIVE: Script allowlist review cadence exists but execution evidence is missing"
}

generate_message := msg if {
    review_execution_verified
    compliant
    msg := "PASS: Authorized scripts are controlled, unauthorized execution is monitored, and allowlist rules are reviewed bi-annually"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
