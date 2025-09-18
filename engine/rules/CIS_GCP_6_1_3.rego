package AutoAudit_tester.rules.CIS_GCP_6_1_3
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_1_3"
title := "MySQL: Ensure 'local_infile' flag is OFF"
policy_group := "Cloud SQL"
blocked_value := "off"

deny := { v |  
  b := input[_]
  r := b.settings.databaseFlags[_]
  q := r.value
  s := r.name
  s == "local_infile"
  q != blocked_value
  v := sprintf("Ensure that local_infile flag is set to %q for MYSQL Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
