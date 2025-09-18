package AutoAudit_tester.rules.CIS_GCP_2_9
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_9"
title        := "Ensure Log Metric Filter and Alerts Exist for VPC Network Changes"
policy_group := "Logging and Monitoring"

deny := { v |
  not vpc_network_metric_exists
  v := sprintf("Project %q: Missing logs-based metric for VPC network create/update/delete", [input.project_id])
} ∪ { v |
  not alert_policy_referencing_user_metric_enabled
  v := sprintf("Project %q: Missing or disabled alert policy for VPC network change metric", [input.project_id])
}

vpc_network_metric_exists {
  some m
  f := input.logging.metrics[_].filter
  contains(f, "compute.networks") or contains(f, "gce_network")
}

alert_policy_referencing_user_metric_enabled {
  some p, c
  p := input.monitoring.alertPolicies[_]
  p.enabled == true
  c := p.conditions[_]
  contains(c.conditionThreshold.filter, "logging.googleapis.com/user/")
}

report := H.build_report(deny, id, title, policy_group)
