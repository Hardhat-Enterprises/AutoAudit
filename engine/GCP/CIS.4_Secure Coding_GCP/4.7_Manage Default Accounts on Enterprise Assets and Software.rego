# METADATA
# title: Manage Default Accounts on Enterprise Assets and Software (GCP)
# description: |
#   Default accounts on enterprise assets and software, including root,
#   administrator, and pre-configured vendor accounts, must be securely
#   managed.
#
#   Default accounts should be disabled, restricted, or otherwise made
#   unusable where they are not required. Where default accounts cannot
#   be disabled, remote access and authentication capabilities must be
#   appropriately restricted.
#
#   Google Cloud implementation uses:
#   - OS Login to replace shared local accounts for VM administration
#   - Hardened VM images to disable or restrict default operating system
#     accounts
#   - OS Config / VM Manager OS Policies to enforce OS account baselines
#   - Organization Policy constraints to restrict service account key
#     creation
#   - Workload Identity Federation where applicable to avoid long-lived
#     service account credentials
#   - IAM reviews to ensure privileged access is individual and revocable
#   - Cloud Audit Logs to provide traceability for privileged activity
#
#   The control verifies:
#   - Default OS accounts are identified and managed
#   - Root/default administrator accounts are disabled or restricted
#   - Remote login using default accounts is prevented where applicable
#   - OS Login is enforced for VM administration
#   - Individual users are associated with IAM identities
#   - Shared administrator identities are not used
#   - Service account key creation is appropriately restricted
#   - Existing service account keys are inventoried
#   - Workload Identity Federation is used where applicable
#   - Privileged IAM access is individually assigned and auditable
#   - Privileged access is periodically reviewed
#   - Access remediation is traceable
#
# related_resources:
# - ref: https://cloud.google.com/compute/docs/oslogin
#   description: OS Login Documentation
# - ref: https://cloud.google.com/compute/docs/images
#   description: Compute Engine Images Documentation
# - ref: https://cloud.google.com/compute/vm-manager/docs/os-policies
#   description: VM Manager OS Policies Documentation
# - ref: https://cloud.google.com/resource-manager/docs/organization-policy/restricting-resources
#   description: Organization Policy Documentation
# - ref: https://cloud.google.com/iam/docs/service-account-keys
#   description: Service Account Keys Documentation
# - ref: https://cloud.google.com/iam/docs/workload-identity-federation
#   description: Workload Identity Federation Documentation
# - ref: https://cloud.google.com/logging/docs/audit
#   description: Cloud Audit Logs Documentation
#
# custom:
#   control_id: CIS-4.7
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.7
#   severity: high
#   service: OS Login / IAM / OS Config
#   asset_type: Users
#   implementation_group: 1
#   requires_permissions:
#   - compute.instances.list
#   - compute.projects.get
#   - osconfig.osPolicyAssignments.list
#   - iam.serviceAccountKeys.list
#   - iam.serviceAccounts.list
#   - resourcemanager.projects.getIamPolicy
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_4_7

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient default account management evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.default_account_management_process_defined == true
    input.default_account_scope_defined == true
    default_account_treatment_verified
    os_login_verified
    service_account_key_controls_verified
    privileged_access_model_verified
    access_review_verified
}

# ---------------------------
# Validate Default Account Scope
# ---------------------------
default_account_scope_defined if {
    input.default_account_scope != ""
    input.default_accounts_identified == true
    input.in_scope_assets_defined == true
}

# ---------------------------
# Validate Default Account Treatment
# ---------------------------
default_account_treatment_verified if {
    input.default_os_accounts_identified == true
    input.default_admin_accounts_restricted == true
    input.root_account_restricted == true
    input.default_remote_login_disabled == true
    input.os_hardening_evidence_available == true
}

# ---------------------------
# Validate OS Login
# ---------------------------
os_login_verified if {
    input.os_login_enabled == true
    input.os_login_enforcement_verified == true
    input.individual_user_ssh_access_verified == true
    input.shared_admin_identity_not_used == true
}

# ---------------------------
# Validate Service Account Key Controls
# ---------------------------
service_account_key_controls_verified if {
    input.service_account_key_creation_restricted == true
    input.service_account_key_inventory_available == true
    input.unmanaged_long_lived_keys_absent == true
}

# ---------------------------
# Validate Workload Identity Federation
# ---------------------------
workload_identity_verified if {
    input.workload_identity_federation_in_scope == false
}

workload_identity_verified if {
    input.workload_identity_federation_in_scope == true
    input.workload_identity_federation_enabled == true
    input.long_lived_external_credentials_avoided == true
}

# ---------------------------
# Validate Privileged Access Model
# ---------------------------
privileged_access_model_verified if {
    input.privileged_access_model_defined == true
    input.group_based_admin_roles == true
    input.individual_privileged_access == true
    input.shared_admin_identities_absent == true
    input.privileged_access_is_revocable == true
}

# ---------------------------
# Validate Access Review
# ---------------------------
access_review_verified if {
    input.privileged_access_review_enabled == true
    input.access_review_record_available == true
    input.access_review_date != ""
    input.access_review_outcome != ""
    input.access_remediation_evidence_available == true
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    default_accounts := get_array(input, "default_accounts")
    service_accounts := get_array(input, "service_accounts")
    service_account_keys := get_array(input, "service_account_keys")
    privileged_bindings := get_array(input, "privileged_iam_bindings")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": default_accounts,
        "details": {
            "default_account_management_process_defined": input.default_account_management_process_defined,
            "default_account_scope": input.default_account_scope,
            "default_accounts_identified": input.default_accounts_identified,
            "default_os_accounts_identified": input.default_os_accounts_identified,
            "default_admin_accounts_restricted": input.default_admin_accounts_restricted,
            "root_account_restricted": input.root_account_restricted,
            "default_remote_login_disabled": input.default_remote_login_disabled,
            "os_hardening_evidence_available": input.os_hardening_evidence_available,
            "os_login_enabled": input.os_login_enabled,
            "os_login_enforcement_verified": input.os_login_enforcement_verified,
            "individual_user_ssh_access_verified": input.individual_user_ssh_access_verified,
            "shared_admin_identity_not_used": input.shared_admin_identity_not_used,
            "service_account_key_creation_restricted": input.service_account_key_creation_restricted,
            "service_account_key_inventory_available": input.service_account_key_inventory_available,
            "unmanaged_long_lived_keys_absent": input.unmanaged_long_lived_keys_absent,
            "workload_identity_federation_in_scope": input.workload_identity_federation_in_scope,
            "workload_identity_federation_enabled": input.workload_identity_federation_enabled,
            "long_lived_external_credentials_avoided": input.long_lived_external_credentials_avoided,
            "privileged_access_model_defined": input.privileged_access_model_defined,
            "group_based_admin_roles": input.group_based_admin_roles,
            "individual_privileged_access": input.individual_privileged_access,
            "shared_admin_identities_absent": input.shared_admin_identities_absent,
            "privileged_access_is_revocable": input.privileged_access_is_revocable,
            "privileged_access_review_enabled": input.privileged_access_review_enabled,
            "access_review_date": input.access_review_date,
            "access_review_outcome": input.access_review_outcome,
            "default_account_count": count(default_accounts),
            "service_account_count": count(service_accounts),
            "service_account_key_count": count(service_account_keys),
            "privileged_binding_count": count(privileged_bindings),
            "requires_sample_evidence": true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
    not input.default_account_management_process_defined
    msg := "FAIL: Default account management process is not defined"
}

generate_message := msg if {
    input.default_account_management_process_defined
    not input.default_account_scope_defined
    msg := "FAIL: Default account scope and affected assets are not defined"
}

generate_message := msg if {
    input.default_account_scope_defined
    not default_account_treatment_verified
    msg := "FAIL: Default OS, administrator, or root accounts are not sufficiently restricted or made unusable"
}

generate_message := msg if {
    default_account_treatment_verified
    not os_login_verified
    msg := "FAIL: OS Login is not enforced or privileged VM access cannot be tied to individual IAM identities"
}

generate_message := msg if {
    os_login_verified
    not service_account_key_controls_verified
    msg := "FAIL: Service account key creation or existing key management is not sufficiently controlled"
}

generate_message := msg if {
    service_account_key_controls_verified
    not workload_identity_verified
    msg := "FAIL: Workload Identity Federation is in scope but long-lived external credentials remain unmanaged"
}

generate_message := msg if {
    workload_identity_verified
    not privileged_access_model_verified
    msg := "FAIL: Privileged access is not individually assigned, group-governed, or revocable"
}

generate_message := msg if {
    privileged_access_model_verified
    not access_review_verified
    msg := "FAIL: Privileged access review or remediation evidence is missing"
}

generate_message := msg if {
    access_review_verified
    compliant
    msg := "PASS: Default accounts are restricted, privileged access is individual and auditable, service account credentials are controlled, and access is periodically reviewed"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
