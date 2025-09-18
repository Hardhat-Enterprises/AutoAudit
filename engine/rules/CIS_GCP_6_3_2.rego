package AutoAudit_tester.rules.CIS_GCP_6_3_2
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_3_2"
title := "SQL Server: 'cross db ownership chaining' = off"
policy_group := "Cloud SQL"
blocked_value := "off"

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "cross db ownership chaining"
  q != blocked_value
  v := sprintf("Ensure that cross db ownership chaining is disabled unless the entire database has it enabled and the attribute is set to the value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
