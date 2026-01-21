import json
import os

RISK_PRIORITY = {
    "High Risk": 3,
    "Concerning": 2,
    "Safe": 1
}

def load_rules():
    path = os.path.join(os.path.dirname(__file__), "rules.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_rules(extracted_data, rules):
    final_risk = "Safe"
    violations = []
    explanation = "No significant legal risk detected."
    fix = "No action required."

    for rule in rules:
        if all(extracted_data.get(k) == v for k, v in rule["conditions"].items()):
            violations.append(rule.get("law"))

            # Upgrade risk if higher
            if RISK_PRIORITY[rule["risk"]] > RISK_PRIORITY[final_risk]:
                final_risk = rule["risk"]
                explanation = rule.get("explanation", explanation)
                fix = rule.get("fix", fix)

    return final_risk, list(set(violations)), explanation, fix
