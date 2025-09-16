package AutoAudit_tester.rules.CIS_GCP_6_3_7
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_3_7"
title := "SQL Server: 'contained database authentication' = off"
policy_group := "Cloud SQL"
blocked_value := "off"

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "contained database authentication"
  q != blocked_value
  v := sprintf("Ensure that contained database are disbaled as an alter any user role owner could retrieve the SQL instance ownership from the db_admin or db_owner. Ensure that the attribute is set to a value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
