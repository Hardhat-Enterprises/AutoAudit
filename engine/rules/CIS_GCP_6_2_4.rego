package AutoAudit_tester.rules.CIS_GCP_6_2_4
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_2_4"
title := "PostgreSQL: 'log_statement' set appropriately (ddl)"
policy_group := "Cloud SQL"
blocked_value := ["ddl", "mod", "none", "all"]

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "log_statement"
  not q in blocked_value
  v := sprintf("Ensure that log_disconnections is set to one of %q, %q, %q or %q for PostgreSQL Instances", [blocked_value[0], blocked_value[1], blocked_value[2], blocked_value[3]])
}


report := H.build_report(deny, id, title, policy_group)
