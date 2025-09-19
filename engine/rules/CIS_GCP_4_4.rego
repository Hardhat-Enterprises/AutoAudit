package AutoAudit_tester.rules.CIS_GCP_4_4
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_4"
title := "Ensure Oslogin Is Enabled for a Project"
policy_group := "Compute"
blocked_value := "false"

deny := { v |
  b := input[_]
  r := b.resourceStatus.effectiveInstanceMetadata.enableOsloginMetadataValue
  r == blocked_value
  v := sprintf("Compute instance should ensure that Oslogin is used to facilitate effective SSH certificate management and the Enable OS Login attribute should not be set to: %q", [r])
}

report := H.build_report(deny, id, title, policy_group)
