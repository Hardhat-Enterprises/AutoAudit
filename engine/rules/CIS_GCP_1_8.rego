package AutoAudit_tester.rules.CIS_GCP_1_8
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_1_8"
title := "Ensure That Separation of Duties Is Enforced While Assigning Service Account Related Roles to Users"
policy_group := "Identity and Access Management"
blocked_roles := ["roles/iam.serviceAccountuser", "roles/iam.serviceAccountAdmin"]

deny := { v |
  b := input.bindings[_]
  r := b.role
  r == blocked_roles
  m := b.members[_]
  v := sprintf("Service account %q must not have role %q", [m, r])
}

report := H.build_report(deny, id, title, policy_group)
