package AutoAudit_tester.rules.CIS_GCP_1_8
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_1_8"
title := "Ensure That Separation of Duties Is Enforced While Assigning Service Account Related Roles to Users"
policy_group := "Identity and Access Management"
blocked_roles := ["roles/iam.serviceAccountuser", "roles/iam.serviceAccountAdmin"]

verification := ` 1. List all users and role assignments:
2. All common users listed under Service_Account_Admin_and_User are
assigned both the roles/iam.serviceAccountAdmin and
roles/iam.serviceAccountUser roles. `

remediation := `1. Go to IAM & Admin/IAM using https://console.cloud.google.com/iam-
admin/iam.
2. For any member having both Service Account Admin and Service account
User roles granted/assigned, click the Delete Bin icon to remove either role
from the member.
Removal of a role should be done based on the business requirements. `

deny := { v |
  b := input.bindings[_]
  r := b.role
  r == blocked_roles
  m := b.members[_]
  v := sprintf("Service account %q must not have role %q", [m, r])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
