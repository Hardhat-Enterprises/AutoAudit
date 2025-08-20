import json
import os

# Load a mock JSON config file
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

# Load all JSON rules from the rules directory
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

# Getting Nested values
def get_value_from_path(config, path):
    placeholder_value = config
    for key in path.split("."):
        if isinstance(placeholder_value, dict):
            placeholder_value = placeholder_value.get(key, {})
        else:
            return None
    return placeholder_value
 

# Evaluate one rule against the config
def evaluate_rule(rule, config):
    expected = rule.get("expected_value")
    value = get_value_from_path(config, rule.get("evaluation_path"))

    if value == expected:
        return True, "Pass"
    return False, f"{rule['tags']} = {value}, expected {expected}"

# Main function to run all rules and show results
def main():
    config = load_mock_config()  # Load tenant configuration
    rules = load_rules()    # Load all CIS rules

    if not config or not rules:
        print("No config or rules found. Exiting.")
        return

    passed, failed = 0, 0

    for rule in rules:
        result, reason = evaluate_rule(rule, config)
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {rule['id_level_2']} - {rule['description']}")
        if not result:
            print(f"  Reason: {reason}")
        passed += result
        failed += not result

    # Summary output
    print("Summary:")
    print(f"  Total Rules: {len(rules)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

if __name__ == "__main__":
    main()