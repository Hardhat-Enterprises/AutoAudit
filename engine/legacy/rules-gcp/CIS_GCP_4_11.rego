package AutoAudit_tester.rules.CIS_GCP_4_11
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_4_11"
title := "Ensure That Compute Instances Have Confidential Computing Enabled"
policy_group := "Compute"
blocked_value := false

verification := `1. List the instances in your project and get details on each instance:
gcloud compute instances list --format=json
2. Ensure that enableConfidentialCompute is set to true for all instances with
machine type starting with "n2d-".
confidentialInstanceConfig:
enableConfidentialCompute: true`

remediation := `Create a new instance with Confidential Compute enabled.
gcloud compute instances create <INSTANCE_NAME> --zone <ZONE> --
confidential-compute --maintenance-policy=TERMINATE`

deny := { v |  
  b := input[_]
  r := b.confidentialInstanceConfig.enableConfidentialCompute
  q := b.confidentialInstanceConfig.confidentialInstanceType
  startswith(q, "n2d")
  r.accessConfigs == blocked_value
  v := sprintf("Compute instance should ensure that there is no Confidential Computing is enabled and the enableConfidentialCompute attribute should be set to: %q for every n2d machine instance", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
