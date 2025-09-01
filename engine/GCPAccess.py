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

crm = build("cloudresourcemanager", "v3", credentials=creds)

project_id = "coastal-stone-470308-a0"
res_name = f"projects/{project_id}"

policy = crm.projects().getIamPolicy(
    resource=res_name,
    body={"options": {"requestedPolicyVersion": 3}}
).execute()

with open("iam_policy.json", "w") as f:
    json.dump(policy, f, indent=2)

