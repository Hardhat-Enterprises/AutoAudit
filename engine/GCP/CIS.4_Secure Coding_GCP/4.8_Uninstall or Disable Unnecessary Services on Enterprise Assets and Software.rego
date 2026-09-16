# METADATA
# title: Uninstall or Disable Unnecessary Services on Enterprise Assets and Software (GCP)
# description: |
#   Unnecessary services, packages, modules, and service functions on
#   enterprise assets must be identified and removed or disabled where
#   they are not required for business operations.
#
#   The purpose of this safeguard is to reduce the attack surface by
#   establishing a repeatable baseline that defines:
#   - Approved services and packages
#   - Prohibited or unnecessary services
#   - Desired state for each unnecessary service
#   - Systems to which the baseline applies
#   - Compliance and remediation requirements
#   - Exception handling requirements
#
#   Google Cloud implementation uses:
#   - OS Config OS Policy Assignments to remove or disable unnecessary
#     packages and services on Compute Engine instances
#   - Hardened golden images to prevent unwanted components from being
#     reintroduced
#   - Artifact Registry practices to maintain approved container base
#     images
#   - Compliance reporting to identify configuration drift
#   - Exception management for approved deviations
#
#   The control verifies:
#   - An approved service/package baseline exists
#   - Unnecessary or prohibited services are identified
#   - OS policies enforce the desired state
#   - OS policies are assigned to the in-scope fleet
#   - Compliance reporting demonstrates coverage
#   - Non-compliant instances are identified
#   - Remediation activity is recorded
#   - Golden images maintain the approved baseline
#   - Exceptions have business justification and expiry
#
# related_resources:
# - ref: https://cloud.google.com/compute/docs/osconfig-management
#   description: VM Manager / OS Config Documentation
# - ref: https://cloud.google.com/compute/docs/os-config-management
#   description: OS Config Management Documentation
# - ref: https://cloud.google.com/artifact-registry/docs
#   description: Artifact Registry Documentation
#
# custom:
#   control_id: CIS-4.8
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.8
#   severity: medium
#   service: OS Config / VM Manager / Artifact Registry
#   asset_type: Devices
#   implementation_group: 2
#   requires_permissions:
#   - compute.instances.list
#   - osconfig.osPolicyAssignments.list
#   - osconfig.osPolicyAssignments.get
#   - osconfig.inventories.get
#   - logging.viewer
#   - logging.logEntries.list
#   - artifactregistry.repositories.list

package cis.gcp_foundations.v2_0_0.control_4_8

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient evidence for unnecessary service management",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    input.service_management_process_defined == true
    input.service_management_scope_defined == true
    baseline_verified
    unnecessary_services_defined
    os_policy_enforcement_verified
    compliance_reporting_verified
    golden_image_baseline_verified
    exception_management_verified
    remediation_evidence_verified
}

# ---------------------------
# Validate Service Management Scope
# ---------------------------
service_management_scope_defined if {
    input.service_management_scope != ""
    input.in_scope_instances_defined == true
    input.in_scope_fleet_count > 0
}

# ---------------------------
# Validate Approved Baseline
# ---------------------------
baseline_verified if {
    input.approved_service_baseline_defined == true
    input.approved_service_list_available == true
    input.prohibited_service_list_available == true
    input.baseline_version != ""
    input.baseline_owner != ""
    input.baseline_last_review_date != ""
}

# ---------------------------
# Validate Unnecessary Services
# ---------------------------
unnecessary_services_defined if {
    input.unnecessary_services_identified == true
    input.unnecessary_services_list_available == true
    input.desired_state_defined == true
}

# ---------------------------
# Validate OS Policy Enforcement
# ---------------------------
os_policy_enforcement_verified if {
    input.os_policy_assignment_defined == true
    input.os_policy_assignment_scope_defined == true
    input.os_policy_targeted_services_defined == true
    input.os_policy_desired_state_defined == true
}

# ---------------------------
# Validate Desired State
# ---------------------------
desired_state_verified if {
    input.unnecessary_service_desired_state == "DISABLED"
}

desired_state_verified if {
    input.unnecessary_service_desired_state == "ABSENT"
}

# ---------------------------
# Validate Compliance Reporting
# ---------------------------
compliance_reporting_verified if {
    input.os_config_compliance_report_available == true
    input.fleet_coverage_reported == true
    input.non_compliant_instances_identified == true
    input.compliance_report_timestamp != ""
}

# ---------------------------
# Validate Compliance Coverage
# ---------------------------
coverage_verified if {
    input.in_scope_instance_count > 0
    input.compliant_instance_count >= 0
    input.non_compliant_instance_count >= 0
    input.in_scope_instance_count ==
        input.compliant_instance_count + input.non_compliant_instance_count
}

# ---------------------------
# Validate Golden Image Baseline
# ---------------------------
golden_image_baseline_verified if {
    input.golden_images_in_scope == false
}

golden_image_baseline_verified if {
    input.golden_images_in_scope == true
    input.golden_image_baseline_defined == true
    input.golden_image_version != ""
    input.golden_image_last_build_date != ""
    input.golden_image_change_control_verified == true
    input.unnecessary_services_excluded_from_image == true
}

# ---------------------------
# Validate Artifact Registry
# ---------------------------
artifact_registry_baseline_verified if {
    input.container_workloads_in_scope == false
}

artifact_registry_baseline_verified if {
    input.container_workloads_in_scope == true
    input.approved_container_base_image_policy_defined == true
    input.container_base_image_inventory_available == true
    input.unapproved_base_images_absent == true
}

# ---------------------------
# Validate Exception Management
# ---------------------------
exception_management_verified if {
    input.exception_process_defined == true

    every exception in input.service_exceptions {
        exception.resource != ""
        exception.service != ""
        exception.business_justification != ""
        exception.approver != ""
        exception.expiry_date != ""
    }
}

exception_management_verified if {
    count(get_array(input, "service_exceptions")) == 0
}

# ---------------------------
# Validate Remediation Evidence
# ---------------------------
remediation_evidence_verified if {
    input.remediation_activity_available == true
    input.remediation_record_id != ""
    input.remediation_date != ""
    input.remediation_owner != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    policy_assignments := get_array(input, "os_policy_assignments")
    prohibited_services := get_array(input, "prohibited_services")
    non_compliant_instances := get_array(input, "non_compliant_instances")
    exceptions := get_array(input, "service_exceptions")
    remediation_records := get_array(input, "remediation_records")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": non_compliant_instances,

        "details": {
            "service_management_process_defined":
                input.service_management_process_defined,

            "service_management_scope":
                input.service_management_scope,

            "in_scope_instances_defined":
                input.in_scope_instances_defined,

            "in_scope_fleet_count":
                input.in_scope_fleet_count,

            "approved_service_baseline_defined":
                input.approved_service_baseline_defined,

            "approved_service_list_available":
                input.approved_service_list_available,

            "prohibited_service_list_available":
                input.prohibited_service_list_available,

            "baseline_version":
                input.baseline_version,

            "baseline_owner":
                input.baseline_owner,

            "baseline_last_review_date":
                input.baseline_last_review_date,

            "unnecessary_services_identified":
                input.unnecessary_services_identified,

            "unnecessary_services_list_available":
                input.unnecessary_services_list_available,

            "desired_state_defined":
                input.desired_state_defined,

            "unnecessary_service_desired_state":
                input.unnecessary_service_desired_state,

            "os_policy_assignment_defined":
                input.os_policy_assignment_defined,

            "os_policy_assignment_scope_defined":
                input.os_policy_assignment_scope_defined,

            "os_policy_targeted_services_defined":
                input.os_policy_targeted_services_defined,

            "os_policy_desired_state_defined":
                input.os_policy_desired_state_defined,

            "os_config_compliance_report_available":
                input.os_config_compliance_report_available,

            "fleet_coverage_reported":
                input.fleet_coverage_reported,

            "non_compliant_instances_identified":
                input.non_compliant_instances_identified,

            "compliance_report_timestamp":
                input.compliance_report_timestamp,

            "in_scope_instance_count":
                input.in_scope_instance_count,

            "compliant_instance_count":
                input.compliant_instance_count,

            "non_compliant_instance_count":
                input.non_compliant_instance_count,

            "golden_images_in_scope":
                input.golden_images_in_scope,

            "golden_image_baseline_defined":
                input.golden_image_baseline_defined,

            "golden_image_version":
                input.golden_image_version,

            "golden_image_last_build_date":
                input.golden_image_last_build_date,

            "golden_image_change_control_verified":
                input.golden_image_change_control_verified,

            "unnecessary_services_excluded_from_image":
                input.unnecessary_services_excluded_from_image,

            "container_workloads_in_scope":
                input.container_workloads_in_scope,

            "approved_container_base_image_policy_defined":
                input.approved_container_base_image_policy_defined,

            "container_base_image_inventory_available":
                input.container_base_image_inventory_available,

            "unapproved_base_images_absent":
                input.unapproved_base_images_absent,

            "exception_process_defined":
                input.exception_process_defined,

            "exception_count":
                count(exceptions),

            "remediation_activity_available":
                input.remediation_activity_available,

            "remediation_record_id":
                input.remediation_record_id,

            "remediation_date":
                input.remediation_date,

            "remediation_owner":
                input.remediation_owner,

            "policy_assignment_count":
                count(policy_assignments),

            "prohibited_service_count":
                count(prohibited_services),

            "non_compliant_instance_count":
                count(non_compliant_instances),

            "remediation_record_count":
                count(remediation_records),

            "requires_sample_evidence":
                true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------

generate_message := msg if {
    not input.service_management_process_defined
    msg := "FAIL: Service and package management process is not defined"
}

generate_message := msg if {
    input.service_management_process_defined
    not input.service_management_scope_defined
    msg := "FAIL: Scope of enterprise assets and services requiring baseline management is not defined"
}

generate_message := msg if {
    input.service_management_scope_defined
    not baseline_verified
    msg := "FAIL: Approved service/package baseline or prohibited-service list is missing or has not been reviewed"
}

generate_message := msg if {
    baseline_verified
    not unnecessary_services_defined
    msg := "FAIL: Unnecessary or prohibited services are not explicitly identified with a required desired state"
}

generate_message := msg if {
    unnecessary_services_defined
    not os_policy_enforcement_verified
    msg := "FAIL: OS Config policy does not demonstrate enforcement of the required service/package state"
}

generate_message := msg if {
    os_policy_enforcement_verified
    not desired_state_verified
    msg := "FAIL: Unnecessary services do not have a desired state of DISABLED or ABSENT"
}

generate_message := msg if {
    desired_state_verified
    not compliance_reporting_verified
    msg := "INCONCLUSIVE: OS policy exists but fleet compliance and non-compliant instance reporting is missing"
}

generate_message := msg if {
    compliance_reporting_verified
    not coverage_verified
    msg := "INCONCLUSIVE: Reported compliance totals do not establish complete fleet coverage"
}

generate_message := msg if {
    coverage_verified
    input.golden_images_in_scope == true
    not golden_image_baseline_verified
    msg := "FAIL: Golden image baseline does not demonstrate exclusion of unnecessary services"
}

generate_message := msg if {
    coverage_verified
    input.container_workloads_in_scope == true
    not artifact_registry_baseline_verified
    msg := "FAIL: Container base image controls do not demonstrate use of approved base images"
}

generate_message := msg if {
    coverage_verified
    not exception_management_verified
    msg := "FAIL: Service exceptions are not controlled with documented justification, approval, and expiry"
}

generate_message := msg if {
    exception_management_verified
    not remediation_evidence_verified
    msg := "INCONCLUSIVE: Non-compliant services are identified but remediation activity cannot be demonstrated"
}

generate_message := msg if {
    remediation_evidence_verified
    compliant
    msg := "PASS: Unnecessary services and packages are defined, managed through enforceable baselines, monitored through compliance reporting, and controlled through time-bound exceptions and remediation"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
    value := obj[key]
} else := []
