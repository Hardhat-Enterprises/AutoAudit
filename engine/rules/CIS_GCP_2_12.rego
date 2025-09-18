package AutoAudit_tester.rules.CIS_GCP_2_12
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_12"
title        := "Ensure That Cloud DNS Logging Is Enabled for All VPC Networks"
policy_group := "Logging and Monitoring"

# Any policy that attaches one or more networks must have enableLogging=true
deny := { v |
  some p
  p := input.dns.policies[_]
  count(p.networks) > 0
  not p.enableLogging
  v := sprintf("Project %q: Cloud DNS policy %q attaches VPCs but logging is disabled", [input.project_id, p.name])
}

report := H.build_report(deny, id, title, policy_group)
