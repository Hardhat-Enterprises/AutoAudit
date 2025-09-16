package AutoAudit_tester.rules.CIS_GCP_6_3_5
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_3_5"
title := "SQL Server: 'remote access' = off"
policy_group := "Cloud SQL"
blocked_value := "off"

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "remote access"
  q != blocked_value
  v := sprintf("Ensure that remote access is not enabled so as to not allow remote execution of stored procedures and the attribute is set to a value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
