"""
Maps rules to compliance frameworks using a mapping table.
"""
import json
 
def load_mapping_table(path="data/framework_crosswalk.json"):
    with open(path, "r") as f:
        return json.load(f)
 
def map_rule_to_frameworks(rule_dict, mapping_table):
    matched_controls = []
    for framework, control_ids in mapping_table.items():
        for control in control_ids:
            if control.lower() in json.dumps(rule_dict).lower():
                matched_controls.append({"framework": framework, "control": control})
    return matched_controls
 
def enrich_rule_with_frameworks(rule_path, mapping_table):
    with open(rule_path, "r") as f:
        rule_data = json.load(f)
    rule_data["frameworks"] = map_rule_to_frameworks(rule_data, mapping_table)
    return rule_data
 
# Example usage
if __name__ == '__main__':
    mapping = load_mapping_table()
    enriched = enrich_rule_with_frameworks("data/sample_rule.json", mapping)
    print(json.dumps(enriched, indent=2))