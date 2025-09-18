package AutoAudit_tester.rules.CIS_GCP_2_8
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_8"
title        := "Ensure Log Metric Filter and Alerts Exist for VPC Route Changes"
policy_group := "Logging and Monitoring"

deny := { v |
  not route_metric_exists
  v := sprintf("Project %q: Missing logs-based metric for VPC route/peering changes", [input.project_id])
} ∪ { v |
  not alert_policy_referencing_user_metric_enabled
  v := sprintf("Project %q: Missing or disabled alert policy for VPC route/peering change metric", [input.project_id])
}

route_metric_exists {
  some m
  f := input.logging.metrics[_].filter
  contains(f, "compute.googleapis.com")
  (
    contains(f, "compute.routes.insert")  or contains(f, "compute.routes.delete") or
    contains(f, "compute.networks.updatePeering")
  )
}

alert_policy_referencing_user_metric_enabled {
  some p, c
  p := input.monitoring.alertPolicies[_]
  p.enabled == true
  c := p.conditions[_]
  contains(c.conditionThreshold.filter, "logging.googleapis.com/user/")
}

report := H.build_report(deny, id, title, policy_group)
