package AutoAudit_tester.rules.CIS_GCP_6_2_7
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_2_7"
title := "PostgreSQL: 'log_min_duration_statement' = -1 (disabled)"
policy_group := "Cloud SQL"
blocked_value := "-1"

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "log_min_duration_statement"
  q != blocked_value
  v := sprintf("Ensure that log_min_duration_statement is disabled and set to the value: %q for PostgreSQL Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
