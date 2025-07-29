import json
import sys

def evaluate_rule(config, rule):
    setting = config.get("MFA", None)
    expected = rule.get("expected_setting")
    if setting == expected:
        return {"rule": rule["id"], "status": "pass"}
    return {"rule": rule["id"], "status": "fail"}

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <config.json> <rule.json>")
        sys.exit(1)

    config_path = sys.argv[1]
    rule_path = sys.argv[2]

    with open(config_path) as f:
        config = json.load(f)

    with open(rule_path) as f:
        rule = json.load(f)

    result = evaluate_rule(config, rule)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
