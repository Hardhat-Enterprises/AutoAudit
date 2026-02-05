package AutoAudit_tester.rules.CIS_GCP_4_8
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_8"
title := "Ensure Compute Instances Are Launched With Shielded VM Enabled"
policy_group := "Compute"
blocked_value := "false"

verification := `1. For each instance in your project, get its metadata:
gcloud compute instances list --format=json | jq -r '. | "vTPM:
\(.[].shieldedInstanceConfig.enableVtpm) IntegrityMonitoring:
\(.[].shieldedInstanceConfig.enableIntegrityMonitoring) Name: \(.[].name)"'
2. Ensure that there is a shieldedInstanceConfig configuration and that
configuration has the enableIntegrityMonitoring and enableVtpm set to
true. If the VM is not a Shield VM image, you will not see a
shieldedInstanceConfig` in the output.`

remediation := `You can only enable Shielded VM options on instances that have Shielded VM support.
For a list of Shielded VM public images, run the gcloud compute images list command
with the following flags:
gcloud compute images list --project gce-uefi-images --no-standard-images
1. Stop the instance:
gcloud compute instances stop <INSTANCE_NAME>
2. Update the instance:
gcloud compute instances update <INSTANCE_NAME> --shielded-vtpm --shielded-
vm-integrity-monitoring
3. Optionally, if you do not use any custom or unsigned drivers on the instance, also
turn on secure boot.
gcloud compute instances update <INSTANCE_NAME> --shielded-vm-secure-boot
4. Restart the instance:
gcloud compute instances start <INSTANCE_NAME> `

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

report := H.build_report(deny, id, title, policy_group, verification, remediation)
