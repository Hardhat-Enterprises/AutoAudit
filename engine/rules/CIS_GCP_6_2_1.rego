package AutoAudit_tester.rules.CIS_GCP_6_2_1
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_2_1"
title := "PostgreSQL: 'log_error_verbosity' DEFAULT or stricter"
policy_group := "Cloud SQL"
blocked_value := ["TERSE", "DEFAULT"]

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "log_error_verbosity"
  not q in blocked_value
  v := sprintf("Ensure that log_error_verbosity is set to either %q or %q for PostgreSQL Instances", [blocked_value[0], blocked_value[1]])
}


report := H.build_report(deny, id, title, policy_group)
