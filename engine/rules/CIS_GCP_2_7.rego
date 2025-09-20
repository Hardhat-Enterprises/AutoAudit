package AutoAudit_tester.rules.CIS_GCP_2_7
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_7"
title        := "Ensure That the Log Metric Filter and Alerts Exist for VPC Network Firewall Rule Changes"
policy_group := "Logging and Monitoring"

deny := { v |
  not firewall_metric_exists
  v := sprintf("Project %q: Missing metric for firewall rule changes", [input.project_id])
} ∪ { v |
  not firewall_alert_enabled_for_user_metric
  v := sprintf("Project %q: Missing or disabled alert policy for firewall rule change metric", [input.project_id])
}

firewall_metric_exists {
  some m
  f := input.logging.metrics[_].filter
  contains(f, "resource.type=\"gce_firewall_rule\"")
  (
    contains(f, "compute.firewalls.insert") or
    contains(f, "compute.firewalls.patch")  or
    contains(f, "compute.firewalls.delete")
  )
}

firewall_alert_enabled_for_user_metric {
  some p, c
  p := input.monitoring.alertPolicies[_]
  p.enabled == true
  c := p.conditions[_]
  filt := c.conditionThreshold.filter else c.filter
  contains(filt, "logging.googleapis.com/user/")
}

report := H.build_report(deny, id, title, policy_group)
