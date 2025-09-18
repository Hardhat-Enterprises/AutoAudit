import json
import os

def load_mock_config(path="engine/test-configs/compliant.json"):
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
 

def evaluate_rule(rule, config):
    expected = rule.get("expected_value")
    value = get_value_from_path(config, rule.get("evaluation_path"))

    if value == expected:
        return True, "Pass"
    return False, f"{rule['tags']} = {value}, expected {expected}"

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