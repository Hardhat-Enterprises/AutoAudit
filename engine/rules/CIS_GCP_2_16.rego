package AutoAudit_tester.rules.CIS_GCP_2_16
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_16"
title        := "Ensure Logging is enabled for HTTP(S) Load Balancer"
policy_group := "Logging and Monitoring"

deny := { v |
  some b
  b := input.compute.backendServices[_]
  not b.logConfig.enable
  v := sprintf("Project %q: Backend service %q has logging disabled", [input.project_id, b.name])
}

report := H.build_report(deny, id, title, policy_group)
