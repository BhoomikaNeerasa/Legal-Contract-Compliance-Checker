import os
import json
import socket
import ollama
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# GROQ CONFIG
# =====================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# =====================================================
# INTERNET CHECK (NON-BLOCKING)
# =====================================================

def internet_available(timeout: int = 3) -> bool:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False


# =====================================================
# SAFE JSON PARSER
# =====================================================

def safe_json_load(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        repaired = text.replace(",}", "}").replace(",]", "]")
        return json.loads(repaired)


# =====================================================
# PROMPT BUILDER — SINGLE CLAUSE (STRICT)
# =====================================================

def build_prompt(clause: str) -> str:
    return f"""
You are a legal clause information extraction system.

CRITICAL INSTRUCTIONS:
1. Return ONLY valid JSON. No explanations.
2. If a topic is NOT discussed in the clause, return null.
3. DO NOT infer missing obligations.
4. TERMINATION RULE:
   - Only fill termination fields if termination is explicitly discussed.
   - Otherwise set termination fields to null.

Schema:
{{
  "clause_type": "data_collection" | "data_sharing" | "data_retention"
               | "refund" | "subscription" | "user_rights"
               | "license" | "employment" | "payment" | "other",

  "collects_personal_data": true | false | null,
  "shares_with_third_parties": true | false | null,
  "consent_clarity": "explicit" | "implicit" | "none" | null,
  "user_data_deletion_right": true | false | null,
  "biometric_data": true | false | null,

  "refund_policy": "none" | "limited" | "clear" | null,
  "auto_renewal": true | false | null,
  "payment_terms_clear": true | false | null,

  "termination_defined": true | false | null,
  "fixed_term": true | false | null,
  "termination_notice_period": true | false | null,
  "cancellation_allowed": true | false | null,

  "data_retention_indefinite": true | false | null,

  "grants_marketing_rights": true | false | null,
  "scope_limited": true | false | null,
  "uses_trademarks": true | false | null
  "working_hours_defined": true | false | null,
"allows_wage_deductions": true | false | null,
"employee_can_terminate": true | false | null,
"leave_entitlement_defined": true | false | null,
"termination_without_compensation": true | false | null
}}

Clause:
\"\"\"{clause}\"\"\"
"""


# =====================================================
# PROMPT BUILDER — BATCH CLAUSE EXTRACTION (STRICT)
# =====================================================

def build_batch_prompt(clauses: list[str]) -> str:
    joined = "\n\n".join(f"Clause {i+1}: {c}" for i, c in enumerate(clauses))

    return f"""
You are a legal clause information extraction system.

CRITICAL INSTRUCTIONS:
1. Return ONLY a valid JSON ARRAY.
2. Each array element corresponds to ONE clause in order.
3. If a topic is NOT discussed in a clause, return null.
4. DO NOT infer missing obligations.
5. TERMINATION RULE:
   - Only fill termination fields if termination is explicitly discussed.
   - Otherwise set termination fields to null.

Schema:
{{
  "clause_type": "data_collection" | "data_sharing" | "data_retention"
               | "refund" | "subscription" | "user_rights"
               | "license" | "employment" | "payment" | "other",

  "collects_personal_data": true | false | null,
  "shares_with_third_parties": true | false | null,
  "consent_clarity": "explicit" | "implicit" | "none" | null,
  "user_data_deletion_right": true | false | null,
  "biometric_data": true | false | null,

  "refund_policy": "none" | "limited" | "clear" | null,
  "auto_renewal": true | false | null,
  "payment_terms_clear": true | false | null,

  "termination_defined": true | false | null,
  "fixed_term": true | false | null,
  "termination_notice_period": true | false | null,
  "cancellation_allowed": true | false | null,

  "data_retention_indefinite": true | false | null,

  "grants_marketing_rights": true | false | null,
  "scope_limited": true | false | null,
  "uses_trademarks": true | false | null
  "working_hours_defined": true | false | null,
"allows_wage_deductions": true | false | null,
"employee_can_terminate": true | false | null,
"leave_entitlement_defined": true | false | null,
"termination_without_compensation": true | false | null

}}

Clauses:
\"\"\"{joined}\"\"\"
"""


# =====================================================
# OLLAMA — SINGLE CLAUSE FALLBACK
# =====================================================

def ollama_extract_single(clause: str) -> dict | None:
    try:
        res = ollama.generate(
            model="llama3.1",
            prompt=build_prompt(clause),
            options={"temperature": 0.0, "num_predict": 300}
        )

        raw = res.get("response", "")
        start, end = raw.find("{"), raw.rfind("}") + 1
        if start == -1 or end == -1:
            return None

        return json.loads(raw[start:end])

    except Exception:
        return None


# =====================================================
# GROQ — BATCH EXTRACTION WITH SAFE FALLBACK
# =====================================================

def groq_batch_extract(clauses: list[str]) -> list[dict]:
    prompt = build_batch_prompt(clauses)

    if internet_available() and groq_client:
        print("⚡ Attempting Groq batch extraction...")
        try:
            completion = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=2200
            )

            print("✅ Groq batch extraction successful")

            parsed = safe_json_load(completion.choices[0].message.content)
            if isinstance(parsed, list):
                return parsed[:len(clauses)]

        except Exception as e:
            print("❌ Groq batch extraction failed:", e)

    print("🖥️ Falling back to Ollama for clause extraction")
    return [ollama_extract_single(c) for c in clauses]



# =====================================================
# CHATBOT — CONTRACT-AWARE LEGAL ASSISTANT
# =====================================================

def chat_with_llm(prompt: str) -> str:
    """
    The prompt already contains:
    - filename
    - decision (SAFE / CONCERNING / HIGH RISK)
    - metadata (contract type, roles)
    - clauses with risks & laws
    """

    if internet_available() and groq_client:
        print("⚡ [CHAT] Trying Groq API...")
        try:
            completion = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert legal contract assistant. Keep answers short and clear.\n\n"
                            "RULES:\n"
                            "1. Answer using the provided contract analysis.\n"
                            "2. Use metadata for contract type and roles.\n"
                            "3. Use final decision to answer if it is safe to sign.\n"
                            "4. List violated laws when risk is CONCERNING or HIGH RISK.\n"
                            "5. Infer carefully when possible and say it is an interpretation.\n"
                            "6. ONLY say 'The contract does not specify this' if nothing can be inferred.\n"
                            "7. Respond politely to thanks or greetings.\n"
                            "8. NEVER invent clauses or legal facts."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.25,
                max_tokens=250
            )

            print("✅ [CHAT] Groq response received")
            return completion.choices[0].message.content.strip()

        except Exception as e:
            print("❌ [CHAT] Groq failed:", e)

    print("🖥️ [CHAT] Falling back to Ollama...")

    # 🔥 FINAL FALLBACK (NO FREEZE)
    try:
        res = ollama.generate(
            model="llama3.1",
            prompt=prompt,
            options={"temperature": 0.25, "num_predict": 200}
        )

        print("✅ [CHAT] Ollama response received")
        return res.get("response", "").strip()

    except Exception as e:
        print("❌ [CHAT] Ollama failed:", e)

    print("⚠️ [CHAT] Both Groq and Ollama failed")
    return "Sorry, I couldn’t process that right now. Please try again."
