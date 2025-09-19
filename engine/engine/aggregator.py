import subprocess, json, sys
from pathlib import Path

RULES = Path("engine/rules")
CONFIGS = Path("engine/test-configs")

policy_map = {
    "CIS_GCP_1_1.rego": "iam_policy.json",
    "CIS_GCP_1_5.rego": "iam_policy.json",
    "CIS_GCP_1_6.rego": "iam_policy.json",
    "CIS_GCP_1_8.rego": "iam_policy.json",

    "CIS_GCP_2_1.rego": "iam_policy.json",

    "CIS_GCP_3_1.rego": "networks.json",
    "CIS_GCP_3_2.rego": "networks.json",
    "CIS_GCP_3_3.rego": "dns_zones.json",
    "CIS_GCP_3_6.rego": "firewalls.json",
    "CIS_GCP_3_7.rego": "firewalls.json",

    "CIS_GCP_4_1.rego": "ComputeInstances.json",
    "CIS_GCP_4_2.rego": "ComputeInstances.json",
    "CIS_GCP_4_3.rego": "ComputeInstances.json",  
    "CIS_GCP_4_4.rego": "ComputeInstances.json",
    "CIS_GCP_4_5.rego": "ComputeInstances.json",
    "CIS_GCP_4_6.rego": "ComputeInstances.json",
    "CIS_GCP_4_8.rego": "ComputeInstances.json",
    "CIS_GCP_4_9.rego": "ComputeInstances.json",
    "CIS_GCP_4_11.rego": "ComputeInstances.json",

    "CIS_GCP_5_1.rego": "bucket_iam_policies.json",

    "CIS_GCP_6_1_2.rego": "sql_instances.json",
    "CIS_GCP_6_1_3.rego": "sql_instances.json",

    "CIS_GCP_6_2_1.rego": "sql_instances.json",
    "CIS_GCP_6_2_2.rego": "sql_instances.json",
    "CIS_GCP_6_2_3.rego": "sql_instances.json",
    "CIS_GCP_6_2_4.rego": "sql_instances.json",
    "CIS_GCP_6_2_5.rego": "sql_instances.json",
    "CIS_GCP_6_2_6.rego": "sql_instances.json",
    "CIS_GCP_6_2_7.rego": "sql_instances.json",
    "CIS_GCP_6_2_8.rego": "sql_instances.json",

    "CIS_GCP_6_3_1.rego": "sql_instances.json",
    "CIS_GCP_6_3_2.rego": "sql_instances.json",
    "CIS_GCP_6_3_3.rego": "sql_instances.json",
    "CIS_GCP_6_3_4.rego": "sql_instances.json",
    "CIS_GCP_6_3_5.rego": "sql_instances.json",
    "CIS_GCP_6_3_6.rego": "sql_instances.json",
    "CIS_GCP_6_3_7.rego": "sql_instances.json",

    "CIS_GCP_6_4.rego":   "sql_instances.json",
    "CIS_GCP_6_5.rego":   "sql_instances.json",
    "CIS_GCP_6_6.rego":   "sql_instances.json",
    "CIS_GCP_6_7.rego":   "sql_instances.json",
    
    "CIS_GCP_7_1.rego": "bigquery_datasets_full.json",
    "CIS_GCP_7_3.rego": "bigquery_datasets_full.json",

    "CIS_GCP_8_1.rego": "dataproc_clusters.json",
}

reports = {}

for rego, config in policy_map.items():
    pkg = Path(rego).stem  
    query = f"data.AutoAudit_tester.rules.{pkg}.report"

    cmd = ["opa", "eval", "-f", "json", "-i", str(CONFIGS/config), "-d" , "engine/engine", "-d", str(RULES/rego), query]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        reports[pkg] = {"error": proc.stderr}
        continue

    try:
        parsed = json.loads(proc.stdout)
        if "result" in parsed and parsed["result"]:
            exprs = parsed["result"][0].get("expressions", [])
            if exprs:
                reports[pkg] = exprs[0].get("value")
            else:
                reports[pkg] = {"error": "No expressions in result"}
        else:
            reports[pkg] = {"error": "No result in OPA output"}
    except Exception as e:
        reports[pkg] = {"error": f"Failed to parse OPA output: {e}"}

output_path = "engine/engine/autoaudit_reports.json"
with open(output_path, "w") as f:
    json.dump(reports, f, indent=2)
print(f"Wrote {output_path}")