package AutoAudit_tester.rules.CIS_GCP_1_5
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_1_5"
title := "Service accounts must not have Owner/Editor"
policy_group := "Identity and Access Management"
blocked_roles := {"roles/editor", "roles/owner"}

deny := { v |
  b := input.bindings[_]
  r := b.role
  r in blocked_roles
  m := b.members[_]
  startswith(m, "serviceAccount:")
  v := sprintf("Service account %q must not have role %q", [m, r])
}

report := H.build_report(deny, id, title, policy_group)
