package AutoAudit_tester.rules.CIS_GCP_7_3
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_7_3"
title := "Ensure a default CMEK is specified for all BigQuery datasets"
policy_group := "BigQuery"
blocked_value := ""

deny := { v |  
  b := input[_]
  r := b.access[_]
  q := r.defaultEncryptionConfiguration.kmsKeyName
  q == blocked_value
  v := sprintf("Ensure that CMEK is exactly sepcified for every BigQuery dataset and that the attribute exists for every BigQuery Instance", [r])
}


report := H.build_report(deny, id, title, policy_group)
