package AutoAudit_tester.rules.CIS_GCP_2_6
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_6"
title        := "Ensure That the Log Metric Filter and Alerts Exist for Custom Role Changes"
policy_group := "Logging and Monitoring"

deny := { v |
  not custom_role_metric_exists
  v := sprintf("Project %q: Missing logs-based metric for IAM custom role changes", [input.project_id])
} ∪ { v |
  not alert_policy_referencing_user_metric_enabled
  v := sprintf("Project %q: Missing or disabled alert policy for IAM custom role change metric", [input.project_id])
}

custom_role_metric_exists {
  some m
  f := input.logging.metrics[_].filter
  contains(f, "google.iam.admin.v1.CreateRole") or
  contains(f, "google.iam.admin.v1.DeleteRole") or
  contains(f, "google.iam.admin.v1.UpdateRole") or
  contains(f, "google.iam.admin.v1.UndeleteRole")
}

alert_policy_referencing_user_metric_enabled {
  some p, c
  p := input.monitoring.alertPolicies[_]
  p.enabled == true
  c := p.conditions[_]
  filt := c.conditionThreshold.filter else c.filter
  contains(filt, "logging.googleapis.com/user/")
}

report := H.build_report(deny, id, title, policy_group)
