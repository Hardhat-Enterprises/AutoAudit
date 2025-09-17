package AutoAudit_tester.rules.CIS_GCP_4_3
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_3"
title := "Ensure “Block Project-Wide SSH Keys” Is Enabled for VM Instances"
policy_group := "Compute"
blocked_value := "false"

deny := { v |
  b := input[_]
  r := b.resourceStatus.effectiveInstanceMetadata.blockProjectSshKeysMetadataValue
  r == blocked_value
  v := sprintf("Compute instance should not use project wide ssh keys and the Block Project-Wide SSH Keys attribute should not be set to: %q", [r])
}

report := H.build_report(deny, id, title, policy_group)
