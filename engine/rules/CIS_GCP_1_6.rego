package AutoAudit_tester.rules.CIS_GCP_1_6
import data.AutoAudit_tester.engine.Helpers as H
import future.keywords.in

id    := "CIS_GCP_1_6"
title := "Ensure That IAM Users Are Not Assigned the Service Account User or Service Account Token Creator Roles at Project"
policy_group := "Identity and Access Management"
blocked_roles := {"roles/iam.serviceAccountuser", "roles/iam.serviceAccountTokenCreator"}

deny := { v |
  b := input.bindings[_]
  r := b.role
  r in blocked_roles
  m := b.members[_]
  startswith(m, "serviceAccount:")
  v := sprintf("Service account %q must not have role %q", [m, r])
}

report := H.build_report(deny, id, title, policy_group)
