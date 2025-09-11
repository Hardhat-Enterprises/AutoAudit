package AutoAudit_tester.rules.CIS_GCP_3_2
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_3_2"
title := "Ensure Legacy Networks Do Not Exist for Older Projects"
policy_group := "Networking"
blocked_value := "LEGACY"

deny := { v |
  b := input[_]
  r := b.routingConfig.bgpBestPathSelectionMode
  r == blocked_value
  v := sprintf("Project network config should not contain %q Networks", [r])
}

report := H.build_report(deny, id, title, policy_group)
