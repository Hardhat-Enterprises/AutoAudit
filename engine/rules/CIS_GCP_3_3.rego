package AutoAudit_tester.rules.CIS_GCP_3_3
import data.AutoAudit_tester.engine.Helpers as H
import future.keywords.in

id    := "CIS_GCP_3_3"
title := " Ensure That DNSSEC Is Enabled for Cloud DNS"
policy_group := "DNS Zones"
blocked_value := "on"

deny := { v |  
  b := input[_]
  r := b.dnssecConfig.state
  r == blocked_value
  v := sprintf("Ensure that dnssecConfig is set to %q", [blocked_value])
}

report := H.build_report(deny, id, title, policy_group)
