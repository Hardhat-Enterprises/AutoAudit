package AutoAudit_tester.rules.CIS_GCP_2_10
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_10"
title        := "Ensure That the Log Metric Filter and Alerts Exist for Cloud Storage IAM Permission Changes"
policy_group := "Logging and Monitoring"

deny := { v |
  not gcs_iam_metric_exists
  v := sprintf("Project %q: Missing metric for Storage IAM permission changes", [input.project_id])
} ∪ { v |
  not gcs_iam_alert_enabled_for_user_metric
  v := sprintf("Project %q: Missing or disabled alert policy for Storage IAM change metric", [input.project_id])
}

gcs_iam_metric_exists {
  some m
  f := input.logging.metrics[_].filter
  contains(f, "storage.setIamPermissions")
}

gcs_iam_alert_enabled_for_user_metric {
  some p, c
  p := input.monitoring.alertPolicies[_]
  p.enabled == true
  c := p.conditions[_]
  filt := c.conditionThreshold.filter else c.filter
  contains(filt, "logging.googleapis.com/user/")
}

report := H.build_report(deny, id, title, policy_group)
