package AutoAudit_tester.rules.CIS_GCP_6_2_3
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_2_3"
title := "PostgreSQL: 'log_disconnections' = on"
policy_group := "Cloud SQL"
blocked_value := "on"

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "log_disconnections"
  q != blocked_value
  v := sprintf("Ensure that log_disconnections is set to either %q for PostgreSQL Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
