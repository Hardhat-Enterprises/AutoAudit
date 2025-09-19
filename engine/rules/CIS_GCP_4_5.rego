package AutoAudit_tester.rules.CIS_GCP_4_5
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_5"
title := "Ensure ‘Enable Connecting to Serial Ports’ Is Not Enabled for VM Instance"
policy_group := "Compute"
blocked_value := "true"

deny := { v |
  b := input[_]
  r := b.resourceStatus.effectiveInstanceMetadata.serialPortEnableMetadataValue
  r == blocked_value
  v := sprintf("Compute instance should ensure that Serial Port Connection is administratively disabled and the Serial port Enable attribute should not be set to: %q", [r])
}

report := H.build_report(deny, id, title, policy_group)
