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
crm_compute = build("compute", "v1", credentials=creds)

project_id = "coastal-stone-470308-a0"
res_name = f"projects/{project_id}"

policy = crm_policy.projects().getIamPolicy(
    resource=res_name,
    body={"options": {"requestedPolicyVersion": 3}}
).execute()

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

with open("iam_policy.json", "w") as f:
    json.dump(policy, f, indent=2)

with open("networks.json", "w") as f:
    json.dump(networks, f, indent=2)

with open("firewalls.json", "w") as f:
    json.dump(firewalls, f, indent=2)

