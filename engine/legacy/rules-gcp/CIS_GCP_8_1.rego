package AutoAudit_tester.rules.CIS_GCP_7_1
import data.AutoAudit_tester.engine.Helpers as H

id    := "CIS_GCP_7_1"
title := "Ensure BigQuery datasets are not anonymously/publicly accessible"
policy_group := "BigQuery"
blocked_value := ["allUsers", "allAuthenticatedUsers"]

verification := `1. Run clusters list command to list all the Dataproc Clusters available in the region:
gcloud dataproc clusters list --region='us-central1'
2. Run clusters describe command to get the key details of the selected cluster:
gcloud dataproc clusters describe <cluster_name> --region=us-central1 --
flatten=config.encryptionConfig.gcePdKmsKeyName
3. 4. If the above command output return "null", then the selected cluster is not
encrypted with Customer managed encryption keys.
Repeat step no. 2 and 3 for other Dataproc Clusters available in the selected
region. Change the region by updating --region and repeat step no. 2 for other
clusters available in the project. Change the project by running the below
command and repeat the audit procedure for other Dataproc clusters available in
other projects:
gcloud config set project <project_ID>"`

remediation := `Before creating cluster ensure that the selected KMS Key have Cloud KMS CryptoKey
Encrypter/Decrypter role assign to Dataproc Cluster service account
("serviceAccount:service-<project_number>@compute-
system.iam.gserviceaccount.com").
Run clusters create command to create new cluster with customer-managed key:
gcloud dataproc clusters create <cluster_name> --region=us-central1 --gce-pd-
kms-key=<key_resource_name>
The above command will create a new cluster in the selected region.
Once the cluster is created migrate all your workloads from the older cluster to the new
cluster and Run clusters delete command to delete cluster:
gcloud dataproc clusters delete <cluster_name> --region=us-central1
Repeat step no. 1 to create a new Dataproc cluster.
Change the project by running the below command and repeat the remediation
procedure for other projects:
gcloud config set project <project_ID>"`

deny := { v |  
  b := input[_]
  r := b.access[_]
  q := r.specialGroup
  q in blocked_value
  v := sprintf("Ensure that users are not granted the role of %q or %q and that the attribute is not set to a value: %q for a BigQuery Instances", [blocked_value[0], blocked_value[1], q])
}


report := H.build_report(deny, id, title, policy_group, verification, remediation)
