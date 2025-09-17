package AutoAudit_tester.rules.CIS_GCP_7_2
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_7_2"
title := "Ensure all BigQuery tables are encrypted with CMEK's"
policy_group := "BigQuery"
blocked_value := ""

deny := { v |  
  b := input[_]
  r := b.tables[_]
  q := r.encryptionConfiguration.kmsKeyName
  q == blocked_value
  v := sprintf("Ensure that BigQuery tables are all encrypted using customer managed encryption and that the attribute exists for a BigQuery Instances", [r])
}


report := H.build_report(deny, id, title, policy_group)
