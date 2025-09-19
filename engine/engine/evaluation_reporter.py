import json

def save_report(results, filename="audit_report.json"):
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)