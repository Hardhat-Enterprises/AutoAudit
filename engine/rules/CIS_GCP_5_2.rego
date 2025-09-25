package AutoAudit_tester.rules.CIS_GCP_5_2
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_5_2"
title := "Ensure That Cloud Storage Buckets Have Uniform Bucket-Level Access Enabled"
policy_group := "Storage"
blocked_value := "false"

verification := `1. List all buckets in a project
gsutil ls
2. For each bucket, verify that uniform bucket-level access is enabled.
gsutil uniformbucketlevelaccess get gs://BUCKET_NAME/
If uniform bucket-level access is enabled, the response looks like:
Uniform bucket-level access setting for gs://BUCKET_NAME/:
Enabled: True
LockedTime: LOCK_DATE `

remediation := `Use the on option in a uniformbucketlevelaccess set command:
gsutil uniformbucketlevelaccess set on gs://BUCKET_NAME/`

deny := { v |  
  b := input[_]
  r := b.iamConfiguration.bucketPolicyOnly.enabled
  r == blocked_value
  v := sprintf("Ensure that Bucket IAM Configuration allows Uniform Bucket Level Access", [r])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
