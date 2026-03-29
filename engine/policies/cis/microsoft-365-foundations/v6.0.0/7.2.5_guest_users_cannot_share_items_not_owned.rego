# METADATA
# title: Ensure that SharePoint guest users cannot share items they don't own
# description: |
#   SharePoint gives users the ability to share files, folders, and site collections. 
#   Internal users can share with external collaborators, and with the right permissions 
#   could share to other external parties.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-7.2.5
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   service: SharePoint
#   requires_permissions:
#   - SharePointTenantSettings.Read.All

package cis.microsoft_365_foundations.v6_0_0.control_7_2_5

default result := {"compliant": false, "message": "Evaluation failed"}

result := {
    "compliant": setting == true,
    "message": generate_message(setting),
    "affected_resources": generate_affected_resources(setting),
    "details": {
        "prevent_external_users_from_resharing": setting,
    },
} if {
    setting := object.get(input, "prevent_external_users_from_resharing", null)
}

generate_message(true) := "Guest users cannot re-share content they do not own"
generate_message(false) := "Guest users can re-share content they do not own"
generate_message(null) := "Unable to determine whether guest users can re-share content they do not own"

generate_affected_resources(true) := []
generate_affected_resources(false) := ["PreventExternalUsersFromResharing is disabled"]
generate_affected_resources(null) := ["PreventExternalUsersFromResharing status unknown"]
