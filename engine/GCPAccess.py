from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth import default
import json

creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
crm = build("cloudresourcemanager", "v3", credentials=creds)

project_id = "coastal-stone-470308-a0"
res_name = f"projects/{project_id}"

policy = crm.projects().getIamPolicy(
    resource=res_name,
    body={"options": {"requestedPolicyVersion": 3}}
).execute()

with open("iam_policy.json", "w") as f:
    json.dump(policy, f, indent=2)

<<<<<<< Updated upstream
=======
print("IAM policy written to iam_policy.json")
>>>>>>> Stashed changes
