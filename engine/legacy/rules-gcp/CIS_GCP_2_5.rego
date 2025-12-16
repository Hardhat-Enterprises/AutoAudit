package AutoAudit_tester.rules.CIS_GCP_2_5
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_5"
title        := "Ensure That the Log Metric Filter and Alerts Exist for Audit Configuration Changes"
policy_group := "Logging and Monitoring"

<<<<<<< HEAD
=======

verification := `1. List the log metrics:
gcloud beta logging metrics list --format json
2. Ensure that the output contains at least one metric with the filter set to:
protoPayload.methodName="SetIamPolicy" AND
protoPayload.serviceData.policyDelta.auditConfigDeltas:*
3. Note the value of the property metricDescriptor.type for the identified metric,
in the format logging.googleapis.com/user/<Log Metric Name>.
Ensure that the prescribed alerting policy is present:
4. List the alerting policies:
gcloud alpha monitoring policies list --format json
5. Ensure that the output contains at least one alert policy where:
• conditions.conditionThreshold.filter is set to
metric.type=\"logging.googleapis.com/user/<Log Metric Name>\"
• AND enabled is set to true`

remediation := `Create a prescribed Log Metric:
• Use the command: gcloud beta logging metrics create
• Reference for command usage:
https://cloud.google.com/sdk/gcloud/reference/beta/logging/metrics/create
Create prescribed Alert Policy
• Use the command: gcloud alpha monitoring policies create
• Reference for command usage:
https://cloud.google.com/sdk/gcloud/reference/alpha/monitoring/policies/create`

>>>>>>> 99b403da (finished final group 2 policy tagging with verification and remediaton)
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

<<<<<<< HEAD
report := H.build_report(deny, id, title, policy_group)
=======
report := H.build_report(deny, id, title, policy_group, verification, remediation)
>>>>>>> 99b403da (finished final group 2 policy tagging with verification and remediaton)
