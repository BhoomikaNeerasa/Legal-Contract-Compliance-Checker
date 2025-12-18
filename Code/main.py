from llm_extractor import extract_with_llm
from durable_rule_engine import load_rules, evaluate_rules
from output_formatter import display_result

def main():
    clause = input("\nEnter clause or terms text:\n> ")
    extracted = extract_with_llm(clause)

    if extracted is None:
        print("\n Could not extract structured data. Please try again.")
        return


    #print("\nExtracted JSON:")
    #print(extracted)

    rules = load_rules()
    risk, laws, explanation, fix = evaluate_rules(extracted, rules)

    print("\n===============FINAL RESULT================")
    print("Risk Level:", risk)
    print("Possible Violations:", laws if laws else "None")
    print("Explanation:", explanation)
    print("Fix:", fix)


if __name__ == "__main__":
    main()
