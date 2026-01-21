def display_result(risk, violations):
    print("\n================ FINAL RESULT ================\n")
    print(f"Risk Level: {risk}")
    print("Possible Violations:", ", ".join(violations) if violations else "None")

    if risk == "High Risk":
        print("Explanation: This clause violates mandatory legal requirements.")
        print("Fix: Add explicit consent, transparency, and user control.")

    elif risk == "Concerning":
        print("Explanation: This clause may be legally risky due to unclear or unfair terms.")
        print("Fix: Clarify terms and limit broad conditions.")

    else:
        print("Explanation: This clause follows standard legal compliance practices.")
        print("Fix: No action required.")
