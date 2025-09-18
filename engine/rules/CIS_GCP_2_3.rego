package AutoAudit_tester.rules.CIS_GCP_2_3
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_3"
title        := "Ensure That Retention Policies on Cloud Storage Buckets Used for Exporting Logs Are Configured Using Bucket Lock"
policy_group := "Logging and Monitoring"

# Flag any export bucket without a locked retention policy (or no positive period)
deny := { v |
  some b
  b := input.storage.buckets[_]
  rp := b.retentionPolicy
  (not rp.isLocked) or (not rp.period) or rp.period <= 0
  v := sprintf("Project %q: Bucket %q retention policy not locked or missing/zero period", [input.project_id, b.name])
}

report := H.build_report(deny, id, title, policy_group)
