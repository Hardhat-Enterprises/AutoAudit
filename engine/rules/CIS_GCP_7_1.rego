package AutoAudit_tester.rules.CIS_GCP_8_1
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_8_1"
title := "Ensure Dataproc clusters are encrypted using CMEK"
policy_group := "Dataproc"
blocked_value := ""

deny := { v |  
  b := input[_]
  r := b.clusters[_]
  q := r.clusterConfig.encryptionConfig.gcePdKmsKeyName
  q == blocked_value
  v := sprintf("Ensure that Dataproc clusters for all regions have CMEK encryptions and that the attribute exists for every Dataproc Instance", [r])
}


report := H.build_report(deny, id, title, policy_group)
