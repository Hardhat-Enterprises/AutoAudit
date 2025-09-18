package AutoAudit_tester.rules.CIS_GCP_2_11
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_11"
title        := "Ensure That the Log Metric Filter and Alerts Exist for SQL Instance Configuration Changes"
policy_group := "Logging and Monitoring"

deny := { v |
  not cloudsql_metric_exists
  v := sprintf("Project %q: Missing metric for Cloud SQL instance updates", [input.project_id])
} ∪ { v |
  not cloudsql_alert_enabled_for_user_metric
  v := sprintf("Project %q: Missing or disabled alert policy for Cloud SQL update metric", [input.project_id])
}

cloudsql_metric_exists {
  some m
  f := input.logging.metrics[_].filter
  contains(f, "cloudsql.instances.update") or contains(f, "cloudsql.instances.patch")
}

cloudsql_alert_enabled_for_user_metric {
  some p, c
  p := input.monitoring.alertPolicies[_]
  p.enabled == true
  c := p.conditions[_]
  filt := c.conditionThreshold.filter else c.filter
  contains(filt, "logging.googleapis.com/user/")
}

report := H.build_report(deny, id, title, policy_group)
