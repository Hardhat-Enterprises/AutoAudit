package AutoAudit_tester.rules.CIS_GCP_4_6
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_6"
title := "Ensure That IP Forwarding Is Not Enabled on Instances"
policy_group := "Compute"
blocked_value := "true"

verification := `1. List all instances:
gcloud compute instances list --format='table(name,canIpForward)'
2. Ensure that CAN_IP_FORWARD column in the output of above command does not
contain True for any VM instance.`

remediation := `1. Use the instances export command to export the existing instance properties:
gcloud compute instances export <INSTANCE_NAME> \
--project <PROJECT_ID> \
--zone <ZONE> \
--destination=<FILE_PATH>
NoteReplace the following:
INSTANCE_NAME the name for the instance that you want to export.
PROJECT_ID: the project ID for this request.
ZONE: the zone for this instance.
FILE_PATH: the output path where you want to save the instance configuration file on
your local workstation.
2. Use a text editor to modify this file
Replace
canIpForward: true
with
canIpForward: false
3. Run this command to import the file you just modified
gcloud compute instances update-from-file INSTANCE_NAME \
--project PROJECT_ID \
--zone ZONE \
--source=FILE_PATH \
--most-disruptive-allowed-action=REFRESH
If the update request is valid and the required resources are available, the instance
update process begins. You can monitor the status of this operation by viewing the audit
logs.
This update requires only a REFRESH not a full restart.`

deny := { v |
  b := input[_]
  r := b.canIpForward
  r == blocked_value
  v := sprintf("Compute instance should ensure that IP Forwarding is administratively disabled and the canIpForward attribute should not be set to: %q", [r])
}

report := H.build_report(deny, id, title, policy_group, verification, remediation)
