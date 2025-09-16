package AutoAudit_tester.rules.CIS_GCP_5_1
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_5_1"
title := "Ensure That Cloud Storage Bucket Is Not Anonymously or Publicly Accessible"
policy_group := "Storage"
blocked_value := ["allUsers" , "allAuthenticatedUsers"]

deny := { v |  
  b := input.bindings[_]
  r := b.members[_]
  r in blocked_value
  v := sprintf("Ensure that Bucket IAM Policy does not allow %q as a role, [r])
}


report := H.build_report(deny, id, title, policy_group)
