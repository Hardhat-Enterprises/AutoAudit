package AutoAudit_tester.rules.CIS_GCP_2_10
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_10"
title        := "Ensure That the Log Metric Filter and Alerts Exist for Cloud Storage IAM Permission Changes"
policy_group := "Logging and Monitoring"

<<<<<<< HEAD
=======
verification := `1. List the log metrics:
gcloud logging metrics list --format json
2. Ensure that the output contains at least one metric with the filter set to:
resource.type=gcs_bucket
AND protoPayload.methodName="storage.setIamPermissions"
3. Note the value of the property metricDescriptor.type for the identified metric,
in the format logging.googleapis.com/user/<Log Metric Name>.
Ensure the prescribed alerting policy is present:
4. List the alerting policies:
gcloud alpha monitoring policies list --format json
5. Ensure that the output contains an least one alert policy where:
• conditions.conditionThreshold.filter is set to
metric.type=\"logging.googleapis.com/user/<Log Metric Name>\"
• AND enabled is set to true`

remediation := `Create the prescribed Log Metric:
• Use the command: gcloud beta logging metrics create
Create the prescribed alert policy:
• Use the command: gcloud alpha monitoring policies create`

>>>>>>> 99b403da (finished final group 2 policy tagging with verification and remediaton)
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

<<<<<<< HEAD
report := H.build_report(deny, id, title, policy_group)
=======
report := H.build_report(deny, id, title, policy_group, verification, remediation)
>>>>>>> 99b403da (finished final group 2 policy tagging with verification and remediaton)
