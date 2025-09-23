package AutoAudit_tester.rules.CIS_GCP_2_16
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_16"
title        := "Ensure Logging is enabled for HTTP(S) Load Balancer"
policy_group := "Logging and Monitoring"

verification := `1. Run the following command
gcloud compute backend-services describe <serviceName>
1. Ensure that enable-logging is enabled and sample rate is set to your desired
level.`

remediation := `1. Run the following command
gcloud compute backend-services update <serviceName> --region=REGION --
enable-logging --logging-sample-rate=<percentageAsADecimal>`

deny := { v |
  some b
  b := input.compute.backendServices[_]
  not b.logConfig.enable
  v := sprintf("Project %q: Backend service %q has logging disabled", [input.project_id, b.name])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
