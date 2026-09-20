# METADATA
# title: Establish and Maintain a Secure Configuration Process (GCP)
# description: |
#   Technical and governance controls must ensure that a documented,
#   approved, and repeatable secure configuration process is established
#   and maintained for enterprise assets and software.
#
#   The secure configuration process must cover:
#   - End-user devices and portable/mobile devices
#   - Non-computing and IoT devices
#   - Servers
#   - Operating systems
#   - Applications and supported software
#
#   The configuration process must be reviewed and updated annually,
#   or when significant enterprise changes occur that could impact
#   the safeguard.
#
#   Google Cloud implementation uses:
#   - Organization Policy constraints to prevent insecure defaults
#   - Standardized secure configuration baselines
#   - Hardened VM images and instance templates
#   - OS Config / VM Manager OS Policies for host-level baseline enforcement
#   - Security Command Center posture and compliance reporting for
#     configuration drift detection
#   - Cloud Audit Logs for configuration change traceability
#   - Cloud Build or CI/CD pipelines for controlled baseline changes
#
#   The control verifies:
#   - A documented secure configuration process exists
#   - Configuration scope is defined
#   - Secure configuration standards are approved and reviewed
#   - Configuration changes are governed and approved
#   - Organization Policy guardrails are enforced
#   - Hardened images or templates are used
#   - Configuration drift is monitored
#   - Deviations have traceable remediation
#   - Secure configuration documentation is reviewed annually
#
# related_resources:
# - ref: https://cloud.google.com/resource-manager/docs/organization-policy/overview
#   description: Organization Policy Documentation
# - ref: https://cloud.google.com/compute/docs/images
#   description: Compute Engine Images Documentation
# - ref: https://cloud.google.com/compute/docs/instance-templates
#   description: Instance Templates Documentation
# - ref: https://cloud.google.com/compute/vm-manager/docs/os-policies
#   description: VM Manager OS Policies Documentation
# - ref: https://cloud.google.com/security-command-center/docs/concepts-security-posture
#   description: Security Command Center Security Posture Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Documentation
# - ref: https://cloud.google.com/build/docs
#   description: Cloud Build Documentation
#
# custom:
#   control_id: CIS-4.1
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.1
#   severity: high
#   service: Organization Policy / OS Config
#   asset_type: Documentation
#   implementation_group: 1
#   requires_permissions:
#   - orgpolicy.policy.get
#   - orgpolicy.policies.list
#   - osconfig.osPolicyAssignments.list
#   - securitycenter.findings.list
#   - logging.viewer
#   - compute.images.list
#   - compute.instanceTemplates.list

package cis.gcp_foundations.v2_0_0.control_4_1

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient secure configuration process evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.secure_configuration_process_defined == true
    input.configuration_scope_defined == true
    secure_configuration_document_verified
    change_governance_verified
    organization_policy_guardrails_verified
    hardened_baseline_verified
    drift_monitoring_verified
    remediation_tracking_verified
    review_execution_verified
}

# ---------------------------
# Validate Secure Configuration Documentation
# ---------------------------
secure_configuration_document_verified if {
    input.secure_configuration_document_title != ""
    input.secure_configuration_document_version != ""
    input.secure_configuration_approval_date != ""
    input.secure_configuration_review_date != ""
    input.roles_responsibilities_defined == true
}

# ---------------------------
# Validate Configuration Scope
# ---------------------------
configuration_scope_defined if {
    input.configuration_scope != ""
    input.cloud_assets_in_scope == true
    input.server_assets_in_scope == true
    input.software_assets_in_scope == true
}

# ---------------------------
# Validate Change Governance
# ---------------------------
change_governance_verified if {
    input.change_control_enabled == true
    input.baseline_change_approval_required == true
    input.change_evidence_available == true
    input.annual_review_attestation_available == true
}

# ---------------------------
# Validate Organization Policy Guardrails
# ---------------------------
organization_policy_guardrails_verified if {
    input.organization_policy_guardrails_enabled == true
    input.organization_policy_scope != ""
    input.effective_policy_values_available == true
}

# ---------------------------
# Validate Hardened Configuration Baselines
# ---------------------------
hardened_baseline_verified if {
    input.hardened_images_or_templates_in_use == true
    input.image_or_template_identifier != ""
    input.image_or_template_last_updated != ""
    input.build_version_history_available == true
}

# ---------------------------
# Validate Drift and Compliance Monitoring
# ---------------------------
drift_monitoring_verified if {
    input.drift_monitoring_enabled == true
    input.compliance_reporting_available == true
    input.sample_scope_defined == true
    input.sample_finding_available == true
}

# ---------------------------
# Validate Remediation Tracking
# ---------------------------
remediation_tracking_verified if {
    input.remediation_process_defined == true
    input.remediation_record_available == true
    input.remediation_status != ""
    input.remediation_timestamp != ""
}

# ---------------------------
# Validate Review Evidence
# ---------------------------
review_execution_verified if {
    input.review_frequency_days <= 365
    input.last_review_timestamp != ""
    input.review_status == "COMPLETED"
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    policies := get_array(input, "organization_policies")
    baselines := get_array(input, "configuration_baselines")
    findings := get_array(input, "drift_findings")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": baselines,
        "details": {
            "secure_configuration_process_defined": input.secure_configuration_process_defined,
            "configuration_scope": input.configuration_scope,
            "secure_configuration_document_title": input.secure_configuration_document_title,
            "secure_configuration_document_version": input.secure_configuration_document_version,
            "secure_configuration_approval_date": input.secure_configuration_approval_date,
            "secure_configuration_review_date": input.secure_configuration_review_date,
            "change_control_enabled": input.change_control_enabled,
            "baseline_change_approval_required": input.baseline_change_approval_required,
            "organization_policy_guardrails_enabled": input.organization_policy_guardrails_enabled,
            "organization_policy_scope": input.organization_policy_scope,
            "hardened_images_or_templates_in_use": input.hardened_images_or_templates_in_use,
            "drift_monitoring_enabled": input.drift_monitoring_enabled,
            "compliance_reporting_available": input.compliance_reporting_available,
            "organization_policy_count": count(policies),
            "configuration_baseline_count": count(baselines),
            "drift_finding_count": count(findings),
            "remediation_process_defined": input.remediation_process_defined,
            "remediation_record_available": input.remediation_record_available,
            "review_frequency_days": input.review_frequency_days,
            "last_review_timestamp": input.last_review_timestamp,
            "review_status": input.review_status,
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.secure_configuration_process_defined
    msg := "FAIL: Secure configuration process is not defined"
}

generate_message := msg if {
    input.secure_configuration_process_defined
    not input.configuration_scope_defined
    msg := "FAIL: Secure configuration scope is not defined"
}

generate_message := msg if {
    input.configuration_scope_defined
    not secure_configuration_document_verified
    msg := "FAIL: Secure configuration standard is missing approval, review, or responsibility evidence"
}

generate_message := msg if {
    secure_configuration_document_verified
    not change_governance_verified
    msg := "FAIL: Secure configuration change governance and approval evidence are not established"
}

generate_message := msg if {
    change_governance_verified
    not organization_policy_guardrails_verified
    msg := "FAIL: Organization Policy guardrails or effective policy evidence are not configured"
}

generate_message := msg if {
    organization_policy_guardrails_verified
    not hardened_baseline_verified
    msg := "FAIL: Hardened images or configuration templates are not sufficiently evidenced"
}

generate_message := msg if {
    hardened_baseline_verified
    not drift_monitoring_verified
    msg := "FAIL: Configuration drift or compliance monitoring is not sufficiently evidenced"
}

generate_message := msg if {
    drift_monitoring_verified
    not remediation_tracking_verified
    msg := "FAIL: Configuration deviation remediation is not traceable"
}

generate_message := msg if {
    remediation_tracking_verified
    not review_execution_verified
    msg := "INCONCLUSIVE: Secure configuration governance exists but annual review execution evidence is missing"
}

generate_message := msg if {
    review_execution_verified
    compliant
    msg := "PASS: Secure configuration process is documented, governed, enforced through GCP guardrails and baselines, monitored for drift, and reviewed annually"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
