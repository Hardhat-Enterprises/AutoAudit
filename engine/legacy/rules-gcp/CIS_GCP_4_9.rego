package AutoAudit_tester.rules.CIS_GCP_4_9
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_9"
title := "Ensure That Compute Instances Do Not Have Public IPAddresses"
policy_group := "Compute"
blocked_value := null

verification := `gcloud compute instances list --format=json
1. The output should not contain an accessConfigs section under
networkInterfaces. Note that the natIP value is present only for instances that
are running or for instances that are stopped but have a static IP address. For
instances that are stopped and are configured to have an ephemeral public IP
address, the natIP field will not be present. Example output:
networkInterfaces:
- accessConfigs:
- kind: compute#accessConfig
name: External NAT
networkTier: STANDARD
type: ONE_TO_ONE_NAT`

remediation := `1. Describe the instance properties:
gcloud compute instances describe <INSTANCE_NAME> --zone=<ZONE>
2. Identify the access config name that contains the external IP address. This
access config appears in the following format:
networkInterfaces:
- accessConfigs:
- kind: compute#accessConfig
name: External NAT
natIP: 130.211.181.55
type: ONE_TO_ONE_NAT
3. Delete the access config.
gcloud compute instances delete-access-config <INSTANCE_NAME> --zone=<ZONE> -
-access-config-name <ACCESS_CONFIG_NAME>
In the above example, the ACCESS_CONFIG_NAME is External NAT. The name of your
access config might be different `

deny := { v |  
  b := input[_]
  r := b.networkInterfaces[_]
  r.accessConfigs != null
  v := sprintf("Compute instance should ensure that there is no Public IP and the accessConfigs section should be set to: %q", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
