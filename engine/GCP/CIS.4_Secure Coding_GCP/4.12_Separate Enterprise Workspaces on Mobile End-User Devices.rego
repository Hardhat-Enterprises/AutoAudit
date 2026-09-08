# METADATA
# title: Separate Enterprise Workspaces on Mobile End-User Devices (GCP)
# description: |
#   Enterprise applications and data must be separated from personal
#   applications and data on supported mobile end-user devices.
#
#   The purpose of this safeguard is to reduce the risk of enterprise
#   information being transferred to personal applications, storage,
#   backups, or services.
#
#   Supported implementations include:
#   - Android Enterprise Work Profile
#   - iOS managed app configuration
#   - Mobile Device Management (MDM) policies
#   - Managed application data protection policies
#   - Conditional access requiring device enrollment and compliance
#
#   Google Cloud provides supporting controls through identity and
#   conditional-access mechanisms. However, the primary workspace
#   separation control is implemented through the organization's endpoint
#   management platform.
#
#   The control verifies:
#   - Mobile device workspace separation is defined
#   - Android Work Profile is enabled where Android devices are supported
#   - iOS managed app configuration is enabled where iOS devices are supported
#   - Policies are assigned to the appropriate user/device groups
#   - Corporate and personal data movement is restricted
#   - Copy/paste restrictions are configured where required
#   - Open-in/save-to-personal restrictions are configured
#   - Backup controls protect enterprise data
#   - Conditional access requires enrolled devices
#   - Conditional access requires compliant devices
#   - Enterprise applications are protected by conditional access
#   - Mobile compliance reporting demonstrates fleet coverage
#   - Non-compliant devices are identified
#   - Exceptions are documented, approved, and time-bound
#
# related_resources:
# - ref: https://www.android.com/enterprise/
#   description: Android Enterprise Documentation
# - ref: https://developers.google.com/android/work/overview
#   description: Android Enterprise Work Profile Documentation
# - ref: https://support.apple.com/guide/deployment/welcome/web
#   description: Apple Platform Deployment Documentation
# - ref: https://cloud.google.com/access-context-manager/docs/overview
#   description: Google Cloud Access Context Manager Documentation
#
# custom:
#   control_id: CIS-4.12
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 4.12
#   severity: medium
#   service: Endpoint Management / Android Enterprise / iOS / Context-Aware Access
#   asset_type: Data
#   implementation_group: 3
#   requires_permissions:
#   - accesscontextmanager.accessPolicies.get
#   - accesscontextmanager.policies.get
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_4_12

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default compliant := false

default result := {
    "compliant": false,
    "message": "Evaluation failed: insufficient enterprise workspace separation evidence",
    "details": {}
}

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
    workspace_separation_process_defined
    mobile_device_scope_defined
    android_controls_verified
    ios_controls_verified
    data_separation_controls_verified
    conditional_access_verified
    compliance_reporting_verified
    exception_management_verified
}

# ---------------------------
# Validate Workspace Separation Process
# ---------------------------
workspace_separation_process_defined if {
    input.workspace_separation_policy_defined == true
    input.enterprise_data_separation_standard_defined == true
    input.supported_mobile_platforms_defined == true
}

# ---------------------------
# Validate Mobile Device Scope
# ---------------------------
mobile_device_scope_defined if {
    input.mobile_device_scope_defined == true
    input.mobile_device_fleet_count > 0
    input.mobile_user_groups_defined == true
}

# ---------------------------
# Validate Android Work Profile
# ---------------------------
android_controls_verified if {
    input.android_devices_in_scope == false
}

android_controls_verified if {
    input.android_devices_in_scope == true
    input.android_work_profile_enabled == true
    input.android_work_profile_assignment_defined == true
    input.android_work_profile_scope_defined == true
    input.android_enterprise_apps_managed == true
}

# ---------------------------
# Validate iOS Managed Configuration
# ---------------------------
ios_controls_verified if {
    input.ios_devices_in_scope == false
}

ios_controls_verified if {
    input.ios_devices_in_scope == true
    input.ios_managed_configuration_enabled == true
    input.ios_managed_app_assignment_defined == true
    input.ios_managed_app_scope_defined == true
    input.ios_enterprise_apps_managed == true
}

# ---------------------------
# Validate Data Separation
# ---------------------------
data_separation_controls_verified if {
    input.data_separation_policy_defined == true
    input.copy_paste_restriction_enabled == true
    input.open_in_restriction_enabled == true
    input.save_to_personal_storage_restricted == true
    input.enterprise_backup_restriction_enabled == true
}

# ---------------------------
# Validate Copy/Paste Restrictions
# ---------------------------
copy_paste_controls_verified if {
    input.copy_paste_restriction_enabled == true
}

# ---------------------------
# Validate Open-In Restrictions
# ---------------------------
open_in_controls_verified if {
    input.open_in_restriction_enabled == true
    input.personal_app_open_in_blocked == true
}

# ---------------------------
# Validate Backup Protection
# ---------------------------
backup_controls_verified if {
    input.enterprise_backup_restriction_enabled == true
    input.personal_backup_of_enterprise_data_blocked == true
}

# ---------------------------
# Validate Conditional Access
# ---------------------------
conditional_access_verified if {
    input.conditional_access_policy_defined == true
    input.device_enrollment_required == true
    input.device_compliance_required == true
    input.enterprise_apps_protected == true
}

# ---------------------------
# Validate Compliance Reporting
# ---------------------------
compliance_reporting_verified if {
    input.mobile_compliance_report_available == true
    input.mobile_fleet_coverage_reported == true
    input.non_compliant_mobile_devices_identified == true
    input.compliance_report_timestamp != ""
}

# ---------------------------
# Validate Fleet Coverage
# ---------------------------
coverage_verified if {
    input.mobile_device_fleet_count > 0
    input.compliant_mobile_device_count >= 0
    input.non_compliant_mobile_device_count >= 0

    input.mobile_device_fleet_count ==
        input.compliant_mobile_device_count +
        input.non_compliant_mobile_device_count
}

# ---------------------------
# Validate Exception Management
# ---------------------------
exception_management_verified if {
    input.exception_process_defined == true

    every exception in input.workspace_separation_exceptions {
        exception.device != ""
        exception.platform != ""
        exception.business_justification != ""
        exception.approver != ""
        exception.expiry_date != ""
    }
}

exception_management_verified if {
    count(get_array(input, "workspace_separation_exceptions")) == 0
}

# ---------------------------
# Validate Enterprise App Protection
# ---------------------------
enterprise_app_protection_verified if {
    input.enterprise_app_inventory_available == true
    input.enterprise_apps_managed == true
    input.enterprise_apps_data_policy_assigned == true
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {

    workspace_policies := get_array(input, "workspace_policies")
    android_profiles := get_array(input, "android_work_profiles")
    ios_configs := get_array(input, "ios_managed_configurations")
    protected_apps := get_array(input, "protected_enterprise_apps")
    non_compliant_devices := get_array(input, "non_compliant_mobile_devices")
    exceptions := get_array(input, "workspace_separation_exceptions")

    output := {
        "compliant": compliant,
        "message": generate_message,
        "affected_resources": non_compliant_devices,

        "details": {
            "workspace_separation_policy_defined":
                input.workspace_separation_policy_defined,

            "enterprise_data_separation_standard_defined":
                input.enterprise_data_separation_standard_defined,

            "supported_mobile_platforms_defined":
                input.supported_mobile_platforms_defined,

            "mobile_device_scope_defined":
                input.mobile_device_scope_defined,

            "mobile_device_fleet_count":
                input.mobile_device_fleet_count,

            "mobile_user_groups_defined":
                input.mobile_user_groups_defined,

            "android_devices_in_scope":
                input.android_devices_in_scope,

            "android_work_profile_enabled":
                input.android_work_profile_enabled,

            "android_work_profile_assignment_defined":
                input.android_work_profile_assignment_defined,

            "android_work_profile_scope_defined":
                input.android_work_profile_scope_defined,

            "android_enterprise_apps_managed":
                input.android_enterprise_apps_managed,

            "ios_devices_in_scope":
                input.ios_devices_in_scope,

            "ios_managed_configuration_enabled":
                input.ios_managed_configuration_enabled,

            "ios_managed_app_assignment_defined":
                input.ios_managed_app_assignment_defined,

            "ios_managed_app_scope_defined":
                input.ios_managed_app_scope_defined,

            "ios_enterprise_apps_managed":
                input.ios_enterprise_apps_managed,

            "data_separation_policy_defined":
                input.data_separation_policy_defined,

            "copy_paste_restriction_enabled":
                input.copy_paste_restriction_enabled,

            "open_in_restriction_enabled":
                input.open_in_restriction_enabled,

            "save_to_personal_storage_restricted":
                input.save_to_personal_storage_restricted,

            "enterprise_backup_restriction_enabled":
                input.enterprise_backup_restriction_enabled,

            "personal_backup_of_enterprise_data_blocked":
                input.personal_backup_of_enterprise_data_blocked,

            "conditional_access_policy_defined":
                input.conditional_access_policy_defined,

            "device_enrollment_required":
                input.device_enrollment_required,

            "device_compliance_required":
                input.device_compliance_required,

            "enterprise_apps_protected":
                input.enterprise_apps_protected,

            "mobile_compliance_report_available":
                input.mobile_compliance_report_available,

            "mobile_fleet_coverage_reported":
                input.mobile_fleet_coverage_reported,

            "non_compliant_mobile_devices_identified":
                input.non_compliant_mobile_devices_identified,

            "compliance_report_timestamp":
                input.compliance_report_timestamp,

            "compliant_mobile_device_count":
                input.compliant_mobile_device_count,

            "non_compliant_mobile_device_count":
                input.non_compliant_mobile_device_count,

            "enterprise_app_inventory_available":
                input.enterprise_app_inventory_available,

            "enterprise_apps_data_policy_assigned":
                input.enterprise_apps_data_policy_assigned,

            "workspace_policy_count":
                count(workspace_policies),

            "android_work_profile_count":
                count(android_profiles),

            "ios_configuration_count":
                count(ios_configs),

            "protected_enterprise_app_count":
                count(protected_apps),

            "non_compliant_device_count":
                count(non_compliant_devices),

            "exception_count":
                count(exceptions),

            "requires_sample_evidence":
                true
        }
    }
}

# ---------------------------
# Message Logic
# ---------------------------

generate_message := msg if {
    not workspace_separation_process_defined
    msg := "FAIL: Enterprise workspace separation policy or supported mobile platform standard is not defined"
}

generate_message := msg if {
    workspace_separation_process_defined
    not mobile_device_scope_defined
    msg := "INCONCLUSIVE: Mobile device fleet and user-group scope cannot be verified"
}

generate_message := msg if {
    mobile_device_scope_defined
    not android_controls_verified
    msg := "FAIL: Android Work Profile is not enabled, assigned, or managed for in-scope Android devices"
}

generate_message := msg if {
    android_controls_verified
    not ios_controls_verified
    msg := "FAIL: iOS managed app configuration is not enabled, assigned, or managed for in-scope iOS devices"
}

generate_message := msg if {
    ios_controls_verified
    not data_separation_controls_verified
    msg := "FAIL: Enterprise-to-personal data sharing restrictions are not sufficiently enforced"
}

generate_message := msg if {
    data_separation_controls_verified
    not enterprise_app_protection_verified
    msg := "FAIL: Enterprise applications are not adequately managed or protected by data-separation policies"
}

generate_message := msg if {
    enterprise_app_protection_verified
    not conditional_access_verified
    msg := "FAIL: Conditional access does not require enrolled and compliant devices for enterprise applications"
}

generate_message := msg if {
    conditional_access_verified
    not compliance_reporting_verified
    msg := "INCONCLUSIVE: Mobile workspace policy exists but fleet compliance reporting is missing"
}

generate_message := msg if {
    compliance_reporting_verified
    not coverage_verified
    msg := "INCONCLUSIVE: Compliance reporting does not establish complete mobile-device fleet coverage"
}

generate_message := msg if {
    coverage_verified
    not exception_management_verified
    msg := "FAIL: Workspace-separation exceptions are not controlled with documented justification, approval, and expiry"
}

generate_message := msg if {
    exception_management_verified
    compliant
    msg := "PASS: Enterprise workspaces are separated on supported mobile devices, enterprise data sharing is restricted, conditional access requires enrolled and compliant devices, and fleet coverage is demonstrated"
}

# ---------------------------
# Helper Functions
# ---------------------------

get_array(obj, key) := value if {
    value := obj[key]
} else := []
