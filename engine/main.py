import json
import os

def load_config(path="test-configs/compliant.json"):
    with open(path) as f:
        return json.load(f)

def load_rules(directory="rules"):
    rules = []
    for file in os.listdir(directory):
        with open(os.path.join(directory, file)) as f:
            rules.append(json.load(f))
    return rules

def evaluate_rule(rule, config):
    expected = rule.get("expected_setting")
    tag = rule.get("tag")

    path_map = {
        "MFA": config.get("azure_ad", {}).get("mfa_status"),
        "LegacyAuth": config.get("azure_ad", {}).get("legacy_authentication"),
        "PhishingProtection": config.get("microsoft_forms", {}).get("phishing_protection"),
    }

    compliant = path_map.get(tag)
    if compliant == expected:
        return True, "Pass"
    else:
        return False, f"{tag} = {compliant}, but expected {expected}"

def main():
    config = load_config()
    rules = load_rules()

    for rule in rules:
        result, reason = evaluate_rule(rule, config)
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {rule['id']} - {rule['description']}")
        if not result:
            print(f"  Reason: {reason}")

if __name__ == "__main__":
    main()