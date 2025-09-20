package AutoAudit_tester.rules.CIS_GCP_2_5
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_5"
title        := "Ensure That the Log Metric Filter and Alerts Exist for Audit Configuration Changes"
policy_group := "Logging and Monitoring"

deny := { v |
  not audit_config_metric_exists
  v := sprintf("Project %q: Missing logs-based metric for audit config changes (SetIamPolicy)", [input.project_id])
} ∪ { v |
  not alert_policy_referencing_user_metric_enabled
  v := sprintf("Project %q: Missing or disabled alert policy for audit-config-change metric", [input.project_id])
}

audit_config_metric_exists {
  some m
  f := input.logging.metrics[_].filter
  contains(f, "protoPayload.methodName=\"SetIamPolicy\"")
  contains(f, "policyDelta.auditConfigDeltas")
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
