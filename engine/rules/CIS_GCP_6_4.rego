package AutoAudit_tester.rules.CIS_GCP_6_4
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_6_4"
title := "Ensure Cloud SQL requires SSL for all incoming connections"
policy_group := "Cloud SQL"
blocked_value := "True"

verification := `1. Get the detailed configuration for every SQL database instance using the
following command:
gcloud sql instances list --format=json
Ensure that section settings: ipConfiguration has the parameter sslMode set to
ENCRYPTED_ONLY`

remediation := `To enforce SSL encryption for an instance run the command:
gcloud sql instances patch INSTANCE_NAME --ssl-mode= ENCRYPTED_ONLY
Note:
RESTART is required for type MySQL Generation 1 Instances (backendType:
FIRST_GEN) to get this configuration in effect`

deny := { v |  
  b := input[_]
  r := b.settings.ipConfiguration.requireSsl
  r != blocked_value
  v := sprintf("Ensure that all incoming connections to the database are enforced with SSL and that the attribute is set to a value: %q for a SQLserver Instances", [blocked_value])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
