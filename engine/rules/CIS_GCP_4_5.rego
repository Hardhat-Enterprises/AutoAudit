package AutoAudit_tester.rules.CIS_GCP_4_5
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_5"
title := "Ensure ‘Enable Connecting to Serial Ports’ Is Not Enabled for VM Instance"
policy_group := "Compute"
blocked_value := "true"

verification := `Ensure the below command's output shows null:
gcloud compute instances describe <vmName> --zone=<region> --
format="json(metadata.items[].key,metadata.items[].value)"
or key and value properties from below command's json response are equal to
serial-port-enable and 0 or false respectively.`

remediation := `Use the below command to disable
gcloud compute instances add-metadata <INSTANCE_NAME> --zone=<ZONE> --
metadata=serial-port-enable=false
or
gcloud compute instances add-metadata <INSTANCE_NAME> --zone=<ZONE> --
metadata=serial-port-enable=0`

deny := { v |
  b := input[_]
  r := b.resourceStatus.effectiveInstanceMetadata.serialPortEnableMetadataValue
  r == blocked_value
  v := sprintf("Compute instance should ensure that Serial Port Connection is administratively disabled and the Serial port Enable attribute should not be set to: %q", [r])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
