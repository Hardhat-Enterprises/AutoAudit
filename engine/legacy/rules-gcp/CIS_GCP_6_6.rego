package AutoAudit_tester.rules.CIS_GCP_6_6
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_6"
title := "Ensure Cloud SQL instances do not have public IPs"
policy_group := "Cloud SQL"
blocked_value := "True"

verification := `1. List all Cloud SQL database instances using the following command:
gcloud sql instances list
2. For every instance of type instanceType: CLOUD_SQL_INSTANCE with
backendType: SECOND_GEN, get detailed configuration. Ignore instances of type
READ_REPLICA_INSTANCE because these instances inherit their settings from the
primary instance. Also, note that first generation instances cannot be configured
to have a private IP address.
gcloud sql instances describe <INSTANCE_NAME>
3. Ensure that the setting ipAddresses has an IP address configured of type:
PRIVATE and has no IP address of type: PRIMARY. PRIMARY IP addresses are
public addresses. An instance can have both a private and public address at the
same time. Note also that you cannot use private IP with First Generation
instances.`

remediation := `1. For every instance remove its public IP and assign a private IP instead:
gcloud sql instances patch <INSTANCE_NAME> --network=<VPC_NETWORK_NAME> --no-
assign-ip
2. Confirm the changes using the following command::
gcloud sql instances describe <INSTANCE_NAME>`

deny := { v |  
  b := input[_]
  r := b.settings.ipConfiguration.ipv4Enabled
  r == blocked_value
  v := sprintf("Ensure that Public Ipv4 is not allocated to a database to reduce attack surface and that the attribute is never set to a value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
