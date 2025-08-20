import json
import os

def load_mock_config(path="test-configs/compliant.json"):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {path}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {path}")
        return {}

def load_rules(directory="rules"):
    rules = []
    for file in os.listdir(directory):
        if file.endswith(".json"):
            try:
                with open(os.path.join(directory, file)) as f:
                    rule = json.load(f)
                    rules.append(rule)
            except json.JSONDecodeError:
                print(f"Invalid JSON in {file}")
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
            print(f"  Description : {rule['description']}")
            print(f"  Reason      : {reason}")
            print(f"  Remediation : {rule['remediation']}")
            print("  --- Risk Assessment ---")
            print(f"  Risk Level  : {rule.get('risk', 'N/A')}")
            print(f"  Impact      : {rule.get('Impact', 'N/A')}")
            print(f"  Likelihood  : {rule.get('Likelihood', 'N/A')}")
            print(f"  Overall     : {rule.get('Risk level', 'N/A')}")
        print("-------------------------------------------------------------------")

        passed += result
        failed += not result

    print(f"\nSummary: {passed} rules passed, {failed} rules failed")
    
if __name__ == "__main__":
    main()