import json
import os
from rule_helpers import match_value, match_in_list, match_regex, match_range
from risk_rating import calculate_impact_level, calculate_risk_level

def evaluate_rule(rule, config):
    value = get_value_from_path(config, rule.get("evaluation_path"))
    expected = rule.get("expected_value")
    match_type = rule.get("match_type", "value")

    if match_type == "value":
        result = match_value(value, expected)
    elif match_type == "in_list":
        result = match_in_list(value, expected)
    elif match_type == "regex":
        result = match_regex(value, expected)
    elif match_type == "range":
        result = match_range(value, tuple(expected))
    else:
        result = False

    if result:
        return True, "Pass", "Low"
    else:
        impact = calculate_impact_level(rule["impact"])
        severity = calculate_risk_level(impact, rule["likelihood"])
        reason = f"{rule['tags']} = {value}, expected {expected} | Severity: {severity}"
        return False, reason, severity

def load_mock_config(path="engine/test-configs/iam_policy.json"):
    with open(path) as f:
        return json.load(f)
    

def load_rules(directory="engine/rules"):
    rules = []
    for file in os.listdir(directory):
        if file.endswith(".json"):
            with open(os.path.join(directory, file)) as f:
                rule = json.load(f)
                rules.append(rule)
    return rules

def get_value_from_path(config, path):
    placeholder_value = config
    for key in path.split("."):
        if isinstance(placeholder_value, dict):
            placeholder_value = placeholder_value.get(key, {})
        else:
            return None
    return placeholder_value
 

def main():
    config = load_mock_config() 
    rules = load_rules()

    passed, failed = 0, 0

    for rule in rules:
        result, reason = evaluate_rule(rule, config)
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {rule['id_level_2']} - {rule['title']}")

        if not result:
            print("")
            print("  --- Cause of Failure --- ")
            print(f"  Description : {rule['description']}")
            print(f"  Reason      : {reason}")
            print(f"  Remediation : {rule['remediation']}")
            print("")
            print("  --- Risk Assessment ---")
            print(f"  Risk Level  : {rule['risk']}")
            print(f"  Impact      : {rule['impact']}")
            print(f"  Likelihood  : {rule['likelihood']}")
            print(f"  Overall     : {rule['risk_level']}")
        print("-------------------------------------------------------------------")

        passed += result
        failed += not result

    print(f"\nSummary: {passed} rules passed, {failed} rules failed")
    
if __name__ == "__main__":
    main()
