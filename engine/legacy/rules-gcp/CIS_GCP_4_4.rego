package AutoAudit_tester.rules.CIS_GCP_4_4
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_4"
title := "Ensure Oslogin Is Enabled for a Project"
policy_group := "Compute"
blocked_value := "false"

verification := `1. List the instances in your project and get details on each instance:
gcloud compute instances list --format=json
2. Verify that the section commonInstanceMetadata has a key enable-oslogin
set to value TRUE.
Exception:
VMs created by GKE should be excluded. These VMs have names that start with
gke- and are labeled goog-gke-node`

remediation := `1. Configure oslogin on the project:
gcloud compute project-info add-metadata --metadata enable-oslogin=TRUE
2. Remove instance metadata that overrides the project setting.
gcloud compute instances remove-metadata <INSTANCE_NAME> --keys=enable-
oslogin
Optionally, you can enable two factor authentication for OS login. For more information,
see: https://cloud.google.com/compute/docs/oslogin/setup-two-factor-authentication.`

deny := { v |
  b := input[_]
  r := b.resourceStatus.effectiveInstanceMetadata.enableOsloginMetadataValue
  r == blocked_value
  v := sprintf("Compute instance should ensure that Oslogin is used to facilitate effective SSH certificate management and the Enable OS Login attribute should not be set to: %q", [r])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
