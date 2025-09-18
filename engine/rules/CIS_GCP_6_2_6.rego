package AutoAudit_tester.rules.CIS_GCP_6_2_6
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_2_6"
title := "PostgreSQL: 'log_min_error_statement' >= ERROR"
policy_group := "Cloud SQL"
blocked_value := ["ERROR", "LOG", "FATAL", "PANIC"]

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "log_min_messages"
  not q in blocked_value
  v := sprintf("Ensure that log_min_error_statement is set to a value above %q like: %q, %q, %q or %q for PostgreSQL Instances", [r, blocked_value[0], blocked_value[1], blocked_value[2], blocked_value[3]])
}


report := H.build_report(deny, id, title, policy_group)
