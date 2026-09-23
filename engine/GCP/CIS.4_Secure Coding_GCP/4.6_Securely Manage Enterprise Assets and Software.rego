# METADATA
# title: Securely Manage Enterprise Assets and Software (GCP)
# description: |
#   Enterprise assets and software must be securely managed through
#   controlled administrative access, secure management protocols, and
#   governed configuration management.
#
#   Configuration should be managed through version-controlled
#   Infrastructure-as-Code (IaC) where applicable. Administrative
#   interfaces must use secure network protocols such as SSH and HTTPS.
#
#   Insecure management protocols such as Telnet and HTTP must not be
#   used unless operationally essential and formally justified.
#
#   Google Cloud implementation uses:
#   - OS Login to centralize SSH identity and reduce unmanaged
#     project-wide SSH keys
#   - Identity-Aware Proxy (IAP) TCP forwarding to provide controlled
#     administrative access without exposing SSH and RDP directly
#     to the internet
#   - HTTPS load balancers with modern TLS policies for web-based
#     administrative interfaces
#   - Organization Policy constraints to restrict insecure network
#     exposure patterns
#   - Cloud Audit Logs for administrative activity and configuration
#     change traceability
#   - Version-controlled Infrastructure-as-Code for configuration
#     management where applicable
#
#   The control verifies:
#   - A secure management standard or runbook exists
#   - Approved management protocols are documented
#   - Telnet and insecure HTTP administration are prohibited
#   - Direct internet SSH/RDP exposure is prohibited or formally justified
#   - OS Login is enabled where SSH administration is applicable
#   - Project-wide unmanaged SSH keys are disabled
#   - IAP TCP forwarding is used for controlled administrative access
#   - Direct public SSH/RDP exposure is avoided
#   - Web administration uses HTTPS and an appropriate TLS policy
#   - Organization Policy guardrails restrict insecure exposure
#   - Administrative actions and changes are traceable
#
# related_resources:
# - ref: https://cloud.google.com/compute/docs/oslogin
#   description: OS Login Documentation
# - ref: https://cloud.google.com/iap/docs/tcp-forwarding-overview
#   description: Identity-Aware Proxy TCP Forwarding Documentation
# - ref: https://cloud.google.com/load-balancing/docs/ssl-policies-concepts
#   description: SSL/TLS Policies Documentation
# - ref: https://cloud.google.com/resource-manager/docs/organization-policy/overview
#   description: Organization Policy Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Documentation
#
# custom:
#   control_id: CIS-4.6
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.6
#   severity: high
#   service: OS Login / Identity-Aware Proxy / HTTPS
#   asset_type: Devices
#   implementation_group: 1
#   requires_permissions:
#   - compute.projects.get
#   - compute.instances.list
#   - compute.firewalls.list
#   - iap.tunnelInstances.accessViaIap
#   - logging.viewer
#   - logging.logEntries.list
#   - orgpolicy.policy.get

package cis.gcp_foundations.v2_0_0.control_4_6

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient secure management evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.secure_management_process_defined == true
    input.management_scope_defined == true
    secure_management_standard_verified
    insecure_protocols_restricted_verified
    os_login_verified
    administrative_access_path_verified
    web_management_security_verified
    direct_management_exposure_verified
    governance_evidence_verified
}

# ---------------------------
# Validate Management Scope
# ---------------------------
management_scope_defined if {
    input.management_scope != ""
    input.administrative_assets_defined == true
    input.management_interfaces_defined == true
}

# ---------------------------
# Validate Secure Management Standard
# ---------------------------
secure_management_standard_verified if {
    input.secure_management_standard_title != ""
    input.secure_management_standard_version != ""
    input.secure_management_standard_approval_date != ""
    input.secure_management_standard_review_date != ""
    input.allowed_management_protocols_defined == true
    input.prohibited_management_protocols_defined == true
}

# ---------------------------
# Validate Insecure Management Protocols
# ---------------------------
insecure_protocols_restricted_verified if {
    input.telnet_prohibited == true
    input.http_admin_prohibited == true
    input.insecure_protocol_exception_process_defined == true
}

# ---------------------------
# Validate OS Login
# ---------------------------
os_login_verified if {
    input.os_login_enabled == true
    input.project_wide_ssh_keys_disabled == true
}

# ---------------------------
# Validate Administrative Access Path
# ---------------------------
administrative_access_path_verified if {
    input.iap_tcp_forwarding_enabled == true
    input.iap_iam_bindings_verified == true
    input.managed_instances_accessible_through_iap == true
}

# ---------------------------
# Validate Web Management Security
# ---------------------------
web_management_security_verified if {
    input.https_management_enabled == true
    input.minimum_tls_version != ""
    input.tls_policy_configured == true
    input.certificate_identifier != ""
}

# ---------------------------
# Validate Direct Management Exposure
# ---------------------------
direct_management_exposure_verified if {
    input.direct_internet_ssh_exposure == false
    input.direct_internet_rdp_exposure == false
    input.management_ports_publicly_exposed == false
}

# ---------------------------
# Validate IaC / Configuration Management
# ---------------------------
iac_configuration_management_verified if {
    input.iac_in_scope == false
}

iac_configuration_management_verified if {
    input.iac_in_scope == true
    input.version_controlled_iac_enabled == true
    input.iac_repository != ""
    input.iac_change_history_available == true
}

# ---------------------------
# Validate Organization Policy Guardrails
# ---------------------------
organization_policy_guardrails_verified if {
    input.organization_policy_guardrails_enabled == true
    input.insecure_exposure_constraints_defined == true
}

# ---------------------------
# Validate Governance Evidence
# ---------------------------
governance_evidence_verified if {
    input.audit_logging_enabled == true
    input.management_access_audit_evidence_available == true
    input.audit_event_timestamp != ""
    input.audit_event_actor != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    management_interfaces := get_array(input, "management_interfaces")
    administrative_assets := get_array(input, "administrative_assets")
    audit_events := get_array(input, "management_audit_events")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": administrative_assets,
        "details": {
            "secure_management_process_defined": input.secure_management_process_defined,
            "management_scope": input.management_scope,
            "secure_management_standard_title": input.secure_management_standard_title,
            "secure_management_standard_version": input.secure_management_standard_version,
            "secure_management_standard_approval_date": input.secure_management_standard_approval_date,
            "secure_management_standard_review_date": input.secure_management_standard_review_date,
            "allowed_management_protocols_defined": input.allowed_management_protocols_defined,
            "prohibited_management_protocols_defined": input.prohibited_management_protocols_defined,
            "telnet_prohibited": input.telnet_prohibited,
            "http_admin_prohibited": input.http_admin_prohibited,
            "insecure_protocol_exception_process_defined": input.insecure_protocol_exception_process_defined,
            "os_login_enabled": input.os_login_enabled,
            "project_wide_ssh_keys_disabled": input.project_wide_ssh_keys_disabled,
            "iap_tcp_forwarding_enabled": input.iap_tcp_forwarding_enabled,
            "iap_iam_bindings_verified": input.iap_iam_bindings_verified,
            "managed_instances_accessible_through_iap": input.managed_instances_accessible_through_iap,
            "https_management_enabled": input.https_management_enabled,
            "minimum_tls_version": input.minimum_tls_version,
            "tls_policy_configured": input.tls_policy_configured,
            "certificate_identifier": input.certificate_identifier,
            "direct_internet_ssh_exposure": input.direct_internet_ssh_exposure,
            "direct_internet_rdp_exposure": input.direct_internet_rdp_exposure,
            "management_ports_publicly_exposed": input.management_ports_publicly_exposed,
            "iac_in_scope": input.iac_in_scope,
            "version_controlled_iac_enabled": input.version_controlled_iac_enabled,
            "iac_repository": input.iac_repository,
            "iac_change_history_available": input.iac_change_history_available,
            "organization_policy_guardrails_enabled": input.organization_policy_guardrails_enabled,
            "insecure_exposure_constraints_defined": input.insecure_exposure_constraints_defined,
            "audit_logging_enabled": input.audit_logging_enabled,
            "management_interface_count": count(management_interfaces),
            "administrative_asset_count": count(administrative_assets),
            "audit_event_count": count(audit_events),
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.secure_management_process_defined
    msg := "FAIL: Secure management process is not defined"
}

generate_message := msg if {
    input.secure_management_process_defined
    not input.management_scope_defined
    msg := "FAIL: Management scope and administrative interfaces are not defined"
}

generate_message := msg if {
    input.management_scope_defined
    not secure_management_standard_verified
    msg := "FAIL: Secure management standard or runbook is missing approval, review, or protocol requirements"
}

generate_message := msg if {
    secure_management_standard_verified
    not insecure_protocols_restricted_verified
    msg := "FAIL: Insecure management protocols are not prohibited or exception handling is not defined"
}

generate_message := msg if {
    insecure_protocols_restricted_verified
    not os_login_verified
    msg := "FAIL: OS Login is not enforced or project-wide SSH keys remain enabled"
}

generate_message := msg if {
    os_login_verified
    not administrative_access_path_verified
    msg := "FAIL: Controlled administrative access through IAP is not sufficiently evidenced"
}

generate_message := msg if {
    administrative_access_path_verified
    not web_management_security_verified
    msg := "FAIL: Web-based management interfaces are not protected by HTTPS and an appropriate TLS policy"
}

generate_message := msg if {
    web_management_security_verified
    not direct_management_exposure_verified
    msg := "FAIL: Direct internet exposure of SSH, RDP, or management ports is present"
}

generate_message := msg if {
    direct_management_exposure_verified
    not iac_configuration_management_verified
    msg := "INCONCLUSIVE: Infrastructure configuration is claimed to use IaC but version control or change history cannot be verified"
}

generate_message := msg if {
    iac_configuration_management_verified
    not organization_policy_guardrails_verified
    msg := "INCONCLUSIVE: Organization Policy guardrails restricting insecure exposure are not sufficiently evidenced"
}

generate_message := msg if {
    organization_policy_guardrails_verified
    not governance_evidence_verified
    msg := "INCONCLUSIVE: Administrative logging exists but traceable management access or change evidence is missing"
}

generate_message := msg if {
    governance_evidence_verified
    compliant
    msg := "PASS: Enterprise assets and software are securely managed using controlled identities, secure management protocols, restricted exposure, and traceable governance"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
