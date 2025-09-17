package AutoAudit_tester.rules.CIS_GCP_6_3_6
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_3_6"
title := "SQL Server: '3625' trace flag = on"
policy_group := "Cloud SQL"
blocked_value := "on"

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "3625"
  q != blocked_value
  v := sprintf("Ensure that log obscuration is enabled through trace flags and the attribute is set to a value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
