package AutoAudit_tester.rules.CIS_GCP_2_4
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_4"
title        := "Ensure Log Metric Filter and Alerts Exist for Project Ownership Changes"
policy_group := "Logging and Monitoring"

deny := { v |
  not project_owner_metric_exists
  v := sprintf("Project %q: Missing logs-based metric for project ownership changes", [input.project_id])
} ∪ { v |
  not alert_policy_referencing_user_metric_enabled
  v := sprintf("Project %q: Missing or disabled alert policy for ownership-change metric", [input.project_id])
}

project_owner_metric_exists {
  some m
  m := input.logging.metrics[_]
  f := m.filter
  contains(f, "cloudresourcemanager.googleapis.com")
  ( contains(f, "ProjectOwnership") or contains(f, "projectOwnerInvitee") or contains(f, "policyDelta.bindingDeltas") )
}

alert_policy_referencing_user_metric_enabled {
  some p, c
  p := input.monitoring.alertPolicies[_]
  p.enabled == true
  c := p.conditions[_]
  contains(c.conditionThreshold.filter, "logging.googleapis.com/user/")
}

report := H.build_report(deny, id, title, policy_group)
