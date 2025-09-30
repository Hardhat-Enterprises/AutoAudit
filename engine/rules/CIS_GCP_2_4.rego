package AutoAudit_tester.rules.CIS_GCP_2_4
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_4"
title        := "Ensure Log Metric Filter and Alerts Exist for Project Ownership Changes"
policy_group := "Logging and Monitoring"

<<<<<<< HEAD
=======
verification := `1. List the log metrics:
gcloud logging metrics list --format json
2. Ensure that the output contains at least one metric with filter set to:
(protoPayload.serviceName="cloudresourcemanager.googleapis.com")
AND (ProjectOwnership OR projectOwnerInvitee)
OR (protoPayload.serviceData.policyDelta.bindingDeltas.action="REMOVE"
AND protoPayload.serviceData.policyDelta.bindingDeltas.role="roles/owner")
OR (protoPayload.serviceData.policyDelta.bindingDeltas.action="ADD"
AND protoPayload.serviceData.policyDelta.bindingDeltas.role="roles/owner")
3. Note the value of the property metricDescriptor.type for the identified metric,
in the format logging.googleapis.com/user/<Log Metric Name>.
4. List the alerting policies:
gcloud alpha monitoring policies list --format json
5. Ensure that the output contains an least one alert policy where:
• conditions.conditionThreshold.filter is set to
metric.type=\"logging.googleapis.com/user/<Log Metric Name>\"
• AND enabled is set to true`

remediation := `Create a prescribed Log Metric:
• Use the command: gcloud beta logging metrics create
• Reference for Command Usage:
https://cloud.google.com/sdk/gcloud/reference/beta/logging/metrics/create
Create prescribed Alert Policy
• Use the command: gcloud alpha monitoring policies create
• Reference for Command Usage:
https://cloud.google.com/sdk/gcloud/reference/alpha/monitoring/policies/create`

>>>>>>> 99b403da (finished final group 2 policy tagging with verification and remediaton)
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

<<<<<<< HEAD
report := H.build_report(deny, id, title, policy_group)
=======
report := H.build_report(deny, id, title, policy_group, verification, remediation)
>>>>>>> 99b403da (finished final group 2 policy tagging with verification and remediaton)
