package AutoAudit_tester.rules.CIS_GCP_1_6
import data.AutoAudit_tester.engine.Helpers as H
import future.keywords.in

id    := "CIS_GCP_1_6"
title := "Ensure That IAM Users Are Not Assigned the Service Account User or Service Account Token Creator Roles at Project"
policy_group := "Identity and Access Management"
blocked_roles := {"roles/iam.serviceAccountuser", "roles/iam.serviceAccountTokenCreator"}
verification := ` To ensure IAM users are not assigned Service Account User role at the project level:
gcloud projects get-iam-policy PROJECT_ID --format json | jq
'.bindings[].role' | grep "roles/iam.serviceAccountUser"
gcloud projects get-iam-policy PROJECT_ID --format json | jq
'.bindings[].role' | grep "roles/iam.serviceAccountTokenCreator"
These commands should not return any output. `

remediation := ` 1. Using a text editor, remove the bindings with the
roles/iam.serviceAccountUser or
roles/iam.serviceAccountTokenCreator.

2. Update the project's IAM policy:
gcloud projects set-iam-policy PROJECT_ID iam.json `

deny := { v |
  b := input.bindings[_]
  r := b.role
  r in blocked_roles
  m := b.members[_]
  startswith(m, "serviceAccount:")
  v := sprintf("Service account %q must not have role %q", [m, r])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
