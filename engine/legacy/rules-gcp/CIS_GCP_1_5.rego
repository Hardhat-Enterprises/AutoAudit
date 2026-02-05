package AutoAudit_tester.rules.CIS_GCP_1_5
import data.AutoAudit_tester.engine.Helpers as H
import future.keywords.in

id    := "CIS_GCP_1_5"
title := "Service accounts must not have Owner/Editor"
policy_group := "Identity and Access Management"
blocked_roles := {"roles/editor", "roles/owner"}
verification := ` From Google Cloud CLI
1. Get the policy that you want to modify, and write it to a JSON file:
Page 27
gcloud projects get-iam-policy PROJECT_ID --format json > iam.json
2. The contents of the JSON file will look similar to the following. Note that role of
members group associated with each serviceaccount does not contain *Admin
or *admin or does not match roles/editor or does not match roles/owner.
This recommendation is only applicable to User-Managed user-created service
accounts. These accounts have the nomenclature:
SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com. Note that some
Google-managed, Google-created service accounts have the same naming format, and
should be excluded (e.g., appsdev-apps-dev-script-
auth@system.gserviceaccount.com which needs the Owner role).`

remediation := `From Google Cloud CLI
1. Export current IAM policy:
   gcloud projects get-iam-policy PROJECT_ID --format=json > iam.json
2. Edit iam.json: remove roles/owner and roles/editor from any serviceAccount:<email> bindings.
3. Apply the updated policy:
   gcloud projects set-iam-policy PROJECT_ID iam.json`

deny := { v |
  b := input.bindings[_]
  r := b.role
  r in blocked_roles
  m := b.members[_]
  startswith(m, "serviceAccount:")
  v := sprintf("Service account %q must not have role %q", [m, r])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
