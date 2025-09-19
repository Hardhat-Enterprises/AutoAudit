package AutoAudit_tester.rules.CIS_GCP_6_3_3
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_3_3"
title := "SQL Server: 'user connections' = 0 (non-limiting)"
policy_group := "Cloud SQL"
blocked_value := "0"

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "user connections"
  q != blocked_value
  v := sprintf("Ensure that simulataneous user connections value is set to default so it utilises the SQL server capabilities to impose the limit and the attribute is set to the value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
