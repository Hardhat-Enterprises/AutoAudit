package AutoAudit_tester.rules.CIS_GCP_4_8
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_8"
title := "Ensure Compute Instances Are Launched With Shielded VM Enabled"
policy_group := "Compute"
blocked_value := "false"

deny[v] if { 
  b := input[_]
  r := b.enableIntegrityMonitoring
  r == blocked_value
  v := sprintf("Compute instance should ensure that Integrity Monitoring is enabled and the enableIntegrityMonitoring attribute should not be set to: %q", [r])
}
deny[v] if { 
  b := input[_]
  q := b.enableVtpm
  q == blocked_value
  v := sprintf("Compute instance should ensure that Vtpm is administratively enabled and the enableVtpm attribute should not be set to: %q", [q])
}

report := H.build_report(deny, id, title, policy_group)
