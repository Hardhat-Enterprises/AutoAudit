package AutoAudit_tester.rules.CIS_GCP_2_2
import data.AutoAudit_tester.engine.Helpers as H

id           := "CIS_GCP_2_2"
title        := "TODO: Set correct CIS 2.2 title"
policy_group := "Logging and Monitoring"

deny := { v |
  false
  v := "TODO 2.2: replace with violation message(s)"
}

report := H.build_report(deny, id, title, policy_group)

