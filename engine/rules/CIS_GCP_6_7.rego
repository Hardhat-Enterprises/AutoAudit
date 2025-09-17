package AutoAudit_tester.rules.CIS_GCP_6_7
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_7"
title := "Ensure Cloud SQL automated backups are enabled"
policy_group := "Cloud SQL"
blocked_value := "True"

deny := { v |  
  b := input[_]
  r := b.settings.backupConfiguration.enabled
  r != blocked_value
  v := sprintf("Ensure that automated backups are always turned on for any SQL server and that the attribute is always set to a value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
