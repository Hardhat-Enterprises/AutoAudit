package AutoAudit_tester.rules.CIS_GCP_5_2
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_5_2"
title := "Ensure That Cloud Storage Buckets Have Uniform Bucket-Level Access Enabled"
policy_group := "Storage"
blocked_value := "false"

deny := { v |  
  b := input[_]
  r := b.iamConfiguration.bucketPolicyOnly.enabled
  r == blocked_value
  v := sprintf("Ensure that Bucket IAM Configuration allows Uniform Bucket Level Access")
}


report := H.build_report(deny, id, title, policy_group)
