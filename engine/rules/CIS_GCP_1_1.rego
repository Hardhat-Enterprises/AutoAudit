package AutoAudit_tester.rules.CIS_GCP_1_1

allowed_email := {"roles/iam.serviceAccountuser", "roles/iam.serviceAccountTokenCreator"}

deny[msg] if {
  b := input.bindings[_]
  r := b.role
  r in blocked_roles
  m := b.members[_]
  msg := sprintf("Service account %q must not have role %q", [m, r])
}