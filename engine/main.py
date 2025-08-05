import json
import os

# Load a JSON config file (mock tenant settings)
def load_config(path="test-configs/compliant.json"):
    """Load the configuration JSON file. Returns an empty dict if file not found or invalid."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {path}")
        return {}
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in config file: {path}")
        return {}

# Load all JSON rules from the rules directory
def load_rules(directory="rules"):
    """Load all JSON rules from the given directory. Skips invalid files."""
    rules = []
    if not os.path.exists(directory):
        print(f"❌ Rules directory not found: {directory}")
        return rules

    for file in os.listdir(directory):
        if file.endswith(".json"):
            try:
                with open(os.path.join(directory, file)) as f:
                    rule = json.load(f)
                    # Validate required keys
                    if all(k in rule for k in ("id", "tag", "expected_setting", "path", "description")):
                        rules.append(rule)
                    else:
                        print(f"⚠️ Skipping {file}: Missing required keys")
            except json.JSONDecodeError:
                print(f"⚠️ Invalid JSON in {file}")
    return rules

# Helper to get nested value using dot notation (e.g. "azure_ad.mfa_status")
def get_value_from_path(config, path):
    """Extract a value from nested JSON using a dot-separated path."""
    keys = path.split(".")
    for key in keys:
        if isinstance(config, dict):
            config = config.get(key, {})
        else:
            return None
    return config if config != {} else None

# Evaluate one rule against the config
def evaluate_rule(rule, config):
    """Compare the expected setting with the actual config value."""
    expected = rule.get("expected_setting")
    value = get_value_from_path(config, rule.get("path"))

    if value == expected:
        return True, "Pass"
    return False, f"{rule['tag']} = {value}, expected {expected}"

# Main function to run all rules and show results
def main():
    config = load_config()  # Load tenant configuration
    rules = load_rules()    # Load all CIS rules

    if not config or not rules:
        print("❌ No config or rules found. Exiting.")
        return

    passed, failed = 0, 0

    for rule in rules:
        result, reason = evaluate_rule(rule, config)
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {rule['id']} - {rule['description']}")
        if not result:
            print(f"  Reason: {reason}")
        passed += result
        failed += not result

    # Summary output
    print("\n📊 Summary:")
    print(f"  Total Rules: {len(rules)}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")

if __name__ == "__main__":
    main()