package AutoAudit_tester.rules.CIS_GCP_2_7
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_7"
title        := "Ensure That the Log Metric Filter and Alerts Exist for VPC Network Firewall Rule Changes"
policy_group := "Logging and Monitoring"

<<<<<<< HEAD
=======
verification := `1. List the log metrics:
gcloud logging metrics list --format json
2. Ensure that the output contains at least one metric with the filter set to:
resource.type="gce_firewall_rule"
AND (protoPayload.methodName:"compute.firewalls.patch"
OR protoPayload.methodName:"compute.firewalls.insert"
OR protoPayload.methodName:"compute.firewalls.delete")
3. Note the value of the property metricDescriptor.type for the identified metric,
in the format logging.googleapis.com/user/<Log Metric Name>.
Ensure that the prescribed alerting policy is present:
4. List the alerting policies:
gcloud alpha monitoring policies list --format json
5. Ensure that the output contains an least one alert policy where:
• conditions.conditionThreshold.filter is set to
metric.type=\"logging.googleapis.com/user/<Log Metric Name>\"
• AND enabled is set to true`

remediation := `Create the prescribed Log Metric
• Use the command: gcloud logging metrics create
Create the prescribed alert policy:
• Use the command: gcloud alpha monitoring policies create`

>>>>>>> 99b403da (finished final group 2 policy tagging with verification and remediaton)
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

<<<<<<< HEAD
report := H.build_report(deny, id, title, policy_group)
=======
report := H.build_report(deny, id, title, policy_group, verification, remediation)
>>>>>>> 99b403da (finished final group 2 policy tagging with verification and remediaton)
