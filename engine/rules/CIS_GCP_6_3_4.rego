package AutoAudit_tester.rules.CIS_GCP_6_3_4
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_3_4"
title := "SQL Server: 'user options' not configured"
policy_group := "Cloud SQL"
blocked_value := ""

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "user options"
  q != blocked_value
  v := sprintf("Ensure that user options flag is not configured because it can be overidden with SET command and the attribute is set to a null string value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
