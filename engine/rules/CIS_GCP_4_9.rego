package AutoAudit_tester.rules.CIS_GCP_4_9
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_9"
title := "Ensure That Compute Instances Do Not Have Public IPAddresses"
policy_group := "Compute"
blocked_value := null

deny := { v |  
  b := input[_]
  r := b.networkInterfaces[_]
  r.accessConfigs != null
  v := sprintf("Compute instance should ensure that there is no Public IP and the accessConfigs section should be set to: %q", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group)
