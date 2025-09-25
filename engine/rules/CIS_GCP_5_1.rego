package AutoAudit_tester.rules.CIS_GCP_5_1
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_5_1"
title := "Ensure That Cloud Storage Bucket Is Not Anonymously or Publicly Accessible"
policy_group := "Storage"
blocked_value := ["allUsers" , "allAuthenticatedUsers"]

verification := ` 1. List all buckets in a project
gsutil ls
2. Check the IAM Policy for each bucket:
gsutil iam get gs://BUCKET_NAME
No role should contain allUsers and/or allAuthenticatedUsers as a member.`

remediation := `Remove allUsers and allAuthenticatedUsers access.
gsutil iam ch -d allUsers gs://BUCKET_NAME
gsutil iam ch -d allAuthenticatedUsers gs://BUCKET_NAME `

deny := { v |  
  b := input.bindings[_]
  r := b.members[_]
  r in blocked_value
  v := sprintf("Ensure that Bucket IAM Policy does not allow %q as a role", [r])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
