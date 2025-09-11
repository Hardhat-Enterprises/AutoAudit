from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth import default
import json 
import os

service_account_info = json.loads(os.environ["GCP_CREDENTIALS"])
creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

crm_policy = build("cloudresourcemanager", "v3", credentials=creds)
bucket_policy = build("storage", "v1", credentials=creds)
crm_compute = build("compute", "v1", credentials=creds)
sqladmin = build("sqladmin", "v1beta4", credentials=creds)
bq = build("bigquery", "v2", credentials=creds)
Dataproc = build("dataproc", "v1", credentials=creds)

project_id = "coastal-stone-470308-a0"
res_name = f"projects/{project_id}"

policy = crm_policy.projects().getIamPolicy(
    resource=res_name,
    body={"options": {"requestedPolicyVersion": 3}}
).execute()

buckets = []
req = bucket_policy.buckets().list(project=project_id)
while req is not None:
    resp = req.execute()
    buckets.extend(resp.get("items", []))
    req = bucket_policy.buckets().list_next(previous_request=req, previous_response=resp)
bucket_iam_policies = []
for b in buckets:
    name = b["name"]
    policy = bucket_policy.buckets().getIamPolicy(
        bucket=name,
        optionsRequestedPolicyVersion=3
    ).execute()
    bucket_iam_policies.append({
        "bucket": name,
        "policy": policy
    })

networks = []
req = crm_compute.networks().list(project=project_id)
while req is not None:
    resp = req.execute()
    networks.extend(resp.get("items", []))
    req = crm_compute.networks().list_next(previous_request=req, previous_response=resp)

firewalls = []
req = crm_compute.firewalls().list(project=project_id)
while req is not None:
    resp = req.execute()
    firewalls.extend(resp.get("items", []))
    req = crm_compute.firewalls().list_next(previous_request=req, previous_response=resp)

instances = []
req = crm_compute.instances().aggregatedList(project=project_id)
while req is not None:
    resp = req.execute()
    for _, scoped in resp.get("items", {}).items():
        instances.extend(scoped.get("instances", [])) 
    req = crm_compute.instances().aggregatedList_next(previous_request=req, previous_response=resp)

sqlinstances = []
req = sqladmin.instances().list(project=project_id)
while req is not None:
    resp = req.execute()
    sqlinstances.extend(resp.get("items", []))
    req = sqladmin.sqlinstances().list_next(previous_request=req, previous_response=resp)

full_datasets = []
req = bq.datasets().list(projectId=project_id, all=True) 
while req is not None:
    resp = req.execute()
    for ds in resp.get("datasets", []):
        ds_ref = ds.get("datasetReference", {})
        ds_id = ds_ref.get("datasetId")
        if not ds_id:
            continue
        
        detail = bq.datasets().get(projectId=project_id, datasetId=ds_id).execute()
        full_datasets.append(detail)

    req = bq.datasets().list_next(previous_request=req, previous_response=resp)

dataproc_clusters = []
req = Dataproc.projects().regions().clusters().list(
    projectId=project_id,
    region="-"
)
while req is not None:
    resp = req.execute()
    dataproc_clusters.extend(resp.get("clusters", []))
    req = Dataproc.projects().regions().clusters().list_next(
        previous_request=req,
        previous_response=resp
    )


with open("iam_policy.json", "w") as f:
    json.dump(policy, f, indent=2)

with open("networks.json", "w") as f:
    json.dump(networks, f, indent=2)

with open("firewalls.json", "w") as f:
    json.dump(firewalls, f, indent=2)

with open("ComputeInstances.json", "w") as f:
    json.dump(instances, f, indent=2)

with open("sql_instances.json", "w") as f:
    json.dump(sqlinstances, f, indent=2)

with open("bigquery_datasets_full.json", "w") as f:
    json.dump(full_datasets, f, indent=2)

with open("dataproc_clusters.json", "w") as f:
    json.dump(dataproc_clusters, f, indent=2)
    
with open("buckets.json", "w") as f:
    json.dump(buckets, f, indent=2)

with open("bucket_iam_policies.json", "w") as f:
    json.dump(bucket_iam_policies, f, indent=2)

