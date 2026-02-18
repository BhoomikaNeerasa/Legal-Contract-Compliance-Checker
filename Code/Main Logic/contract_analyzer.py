import PyPDF2
import re
from docx import Document
from llm_extractor import groq_batch_extract
from durable_rule_engine import load_rules, evaluate_rules

LEGAL_KEYWORDS = [
    "rent", "payment", "termination",
    "employment", "salary", "overtime",
    "privacy", "personal data",
    "refund", "subscription",
    "arbitration", "jurisdiction",
    "license", "trademark", "marketing"
]


# =====================================================
# NORMALIZATION LAYER (ADDED)
# =====================================================

def normalize_extraction(data: dict) -> dict:
    if data.get("uses_trademarks") is True:
        data["grants_marketing_rights"] = True

    if data.get("grants_marketing_rights") is True and data.get("scope_limited") is None:
        data["scope_limited"] = False

    if (
        data.get("clause_type") in ["data_retention", "user_rights"]
        and data.get("data_retention_indefinite") is None
    ):
        data["data_retention_indefinite"] = True
    # 🔥 EMPLOYMENT TERMINATION NORMALIZATION
    if data.get("clause_type") == "employment":
    # If termination is mentioned but notice period is missing → assume no notice
        if data.get("termination_defined") is True and data.get("termination_notice_period") is None:
            data["termination_notice_period"] = False

    # If termination defined but cancellation rights unclear → employer only
    if data.get("termination_defined") is True and data.get("cancellation_allowed") is None:
        data["cancellation_allowed"] = False


    return data


# =====================================================
# FILE EXTRACTION
# =====================================================

def extract_text(path):
    if path.endswith(".txt"):
        return open(path, "r", encoding="utf-8", errors="ignore").read()

    if path.endswith(".pdf"):
        text = ""
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    if path.endswith(".docx"):
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    return ""


def split_clauses(text):
    clauses = []

    # 1️⃣ Split by numbered sections if present
    numbered = re.split(r"\n\s*(\d+\.\s+)", text)
    if len(numbered) > 1:
        buffer = ""
        for part in numbered:
            if re.match(r"\d+\.\s+", part):
                if buffer.strip():
                    clauses.append(buffer.strip())
                buffer = part
            else:
                buffer += part
        if buffer.strip():
            clauses.append(buffer.strip())

    # 2️⃣ Fallback: split by legal sentence boundaries
    if not clauses:
        clauses = re.split(
            r"(?<=\.)\s+(?=(The Employer|The Employee|The Company|Either party))",
            text
        )

    # 3️⃣ Final cleanup
    return [c.strip() for c in clauses if len(c.strip()) > 80]


# =====================================================
# 🔥 ADDED: CONTRACT METADATA FOR CHATBOT
# =====================================================

def extract_contract_metadata(text: str) -> dict:
    lower = text.lower()
    contract_type = "General Contract"

    if "employment" in lower or "employer" in lower:
        contract_type = "Employment Agreement"
    elif "web development" in lower or "developer" in lower:
        contract_type = "Web Development Agreement"
    elif "rent" in lower or "tenant" in lower:
        contract_type = "Rental / Lease Agreement"
    elif "partnership" in lower:
        contract_type = "Partnership Agreement"
    elif "sponsor" in lower:
        contract_type = "Sponsorship Agreement"

    return {
        "contract_type": contract_type,
        "mentions_employer": "employer" in lower,
        "mentions_employee": "employee" in lower,
        "mentions_client": "client" in lower,
        "mentions_service_provider": "developer" in lower or "provider" in lower
    }


# =====================================================
# MAIN ANALYSIS PIPELINE
# =====================================================

def analyze_contract(path):
    print("📦 analyze_contract called")
    text = extract_text(path)

    # 🔥 ADDED
    metadata = extract_contract_metadata(text)

    clauses = split_clauses(text)
    rules = load_rules()

    filtered = [
        c for c in clauses
        if any(k in c.lower() for k in LEGAL_KEYWORDS)
    ]

    extracted_list = groq_batch_extract(filtered)
    # ---------- EDS (once per contract) ----------
    '''
    if filtered:
        clause = filtered[0]  # test first relevant clause

        outputs = []
        for _ in range(3):
            outputs.append(groq_batch_extract([clause])[0])

        def norm(o):
            return str(sorted(o.items()))

        ref = norm(outputs[0])
        same = sum(1 for o in outputs if norm(o) == ref)

        eds = same / len(outputs)
        print(f"\n📊 EDS (Extraction Determinism Score): {eds:.3f}\n") 
        '''

    required_fields = {
    "clause_type",
    "collects_personal_data",
    "shares_with_third_parties",
    "consent_clarity",
    "refund_policy",
    "termination_defined"
}

    valid = 0
    for item in extracted_list:
        if item and all(f in item for f in required_fields):
            valid += 1

    print("\n📦 SCHEMA COMPLIANCE REPORT")
    print(f"   JSON objects returned : {len(extracted_list)}")
    print(f"   Schema valid objects  : {valid}")
    print(f"   SCR                   : {valid / len(extracted_list) if extracted_list else 0:.3f}\n")

    
    results = []
    highest_risk = "Safe"
    seen_contract_level_rules = set()

    for clause, extracted in zip(filtered, extracted_list):

        if not extracted:
            continue

        extracted = normalize_extraction(extracted)
        risk, laws, explanation, fix, rule_id = evaluate_rules(extracted, rules)
        if risk != "Safe":
            print("⚠️ Rule triggered for clause")


        if rule_id == "EMPLOYMENT_NO_NOTICE_PERIOD":
            if rule_id in seen_contract_level_rules:
                continue
            seen_contract_level_rules.add(rule_id)
    
        if risk == "High Risk":
            highest_risk = "High Risk"
        elif risk == "Concerning" and highest_risk != "High Risk":
            highest_risk = "Concerning"

        results.append({
            "clause": clause[:400],
            "risk": risk,
            "laws": laws,
            "explanation": explanation,
            "fix": fix
        })
    triggered = sum(1 for r in results if r["risk"] != "Safe")

    print("\n📜 RULE ACTIVATION SUMMARY")
    print(f"   Clauses evaluated : {len(results)}")
    print(f"   Rules triggered   : {triggered}")
    print(f"   RAA               : {triggered / len(results) if results else 0:.3f}\n")


    if highest_risk == "High Risk":
        decision_text = "❌ HIGH RISK: You should NOT sign this contract."
    elif highest_risk == "Concerning":
        decision_text = "⚠️ CONCERNING: Review carefully and seek clarification before proceeding."
    else:
        decision_text = "✅ SAFE: You may proceed with signing."

    # 🔥 EXTENDED RETURN (NOT REPLACED)
    return results, decision_text, highest_risk, text, metadata
