package AutoAudit_tester.rules.CIS_GCP_7_3
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_7_3"
title := "Ensure a default CMEK is specified for all BigQuery datasets"
policy_group := "BigQuery"
blocked_value := ""

verification := `List all dataset names
bq ls
Use the following command to view each dataset details.
bq show <data_set_object>
Verify the kmsKeyName is present.`

remediation := `The default CMEK for existing data sets can be updated by specifying the default key in
the EncryptionConfiguration.kmsKeyName field when calling the datasets.insert
or datasets.patch methods`

deny := { v |  
  b := input[_]
  r := b.access[_]
  q := r.defaultEncryptionConfiguration.kmsKeyName
  q == blocked_value
  v := sprintf("Ensure that CMEK is exactly sepcified for every BigQuery dataset and that the attribute exists for every BigQuery Instance", [r])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
