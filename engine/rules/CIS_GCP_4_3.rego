package AutoAudit_tester.rules.CIS_GCP_4_3
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_3"
title := "Ensure “Block Project-Wide SSH Keys” Is Enabled for VM Instances"
policy_group := "Compute"
blocked_value := "false"

verification := `1. List the instances in your project and get details on each instance:
gcloud compute instances list --format=json
2. Ensure key: block-project-ssh-keys is set to value: 'true'.`

remediation := ` To block project-wide public SSH keys, set the metadata value to TRUE:
gcloud compute instances add-metadata <INSTANCE_NAME> --metadata block-
project-ssh-keys=TRUE `

deny := { v |
  b := input[_]
  r := b.resourceStatus.effectiveInstanceMetadata.blockProjectSshKeysMetadataValue
  r == blocked_value
  v := sprintf("Compute instance should not use project wide ssh keys and the Block Project-Wide SSH Keys attribute should not be set to: %q", [r])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
