package AutoAudit_tester.rules.CIS_GCP_2_8
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_8"
title        := "Ensure Log Metric Filter and Alerts Exist for VPC Route Changes"
policy_group := "Logging and Monitoring"

<<<<<<< HEAD
=======
verification := `1. List the log metrics:
gcloud logging metrics list --format json
2. Ensure that the output contains at least one metric with the filter set to:
resource.type="gce_route"
AND (protoPayload.methodName:"compute.routes.delete"
OR protoPayload.methodName:"compute.routes.insert")
3. Note the value of the property metricDescriptor.type for the identified metric,
in the format logging.googleapis.com/user/<Log Metric Name>.
Ensure that the prescribed alerting policy is present:
4. List the alerting policies:
gcloud alpha monitoring policies list --format json
5. Ensure that the output contains an least one alert policy where:
• conditions.conditionThreshold.filter is set to
metric.type=\"logging.googleapis.com/user/<Log Metric Name>\"
• AND enabled is set to true`

remediation := `Create the prescribed Log Metric:
• Use the command: gcloud logging metrics create
Create the prescribed the alert policy:
• Use the command: gcloud alpha monitoring policies create`

>>>>>>> 99b403da (finished final group 2 policy tagging with verification and remediaton)
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

<<<<<<< HEAD
report := H.build_report(deny, id, title, policy_group)
=======
report := H.build_report(deny, id, title, policy_group, verification, remediation)
>>>>>>> 99b403da (finished final group 2 policy tagging with verification and remediaton)
