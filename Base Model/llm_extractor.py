import ollama
import json

def extract_with_llm(clause: str) -> dict:
    prompt = f"""
You are an information extraction system.

Extract facts from the legal clause and return ONLY valid JSON
matching this schema:

{{
  "clause_type": "data_collection" | "data_sharing" | "data_retention" | "refund" | "subscription" | "user_rights" | "other",
  "collects_personal_data": true | false,
  "shares_with_third_parties": true | false,
  "consent_clarity": "explicit" | "implicit" | "none",
  "user_data_deletion_right": true | false,
  "biometric_data": true | false,
  "refund_policy": "none" | "limited" | "clear",
  "auto_renewal": true | false,
  "data_retention_indefinite": true | false
}}

Rules:
- Determine clause_type based on primary intent of the clause.
- If the clause mentions refunds, payments, cancellations, or final sale terms,
  set clause_type = "refund".
- If the clause contains "no refund", "no refunds", "all purchases are final",
  set refund_policy = "none".
- Use "data_collection" only for data collection clauses.
- Use "data_sharing" only for sharing clauses.
- Use "data_retention" only for retention clauses.

Clause:
\"\"\"{clause}\"\"\"

Return ONLY JSON. No explanation.
"""

    try:
        response = ollama.generate(model="llama3.1", prompt=prompt)
        raw = response.get("response", "").strip()

        #  Prevent empty response crash
        if not raw:
            raise ValueError("Empty response from LLM")

        #  Extract only JSON if extra text exists
        start = raw.find("{")
        end = raw.rfind("}") + 1
        json_text = raw[start:end]

        return json.loads(json_text)

    except json.JSONDecodeError:
        print("\n ERROR: LLM returned invalid JSON.")
        print("Raw response:\n", raw)
        return None

    except Exception as e:
        print("\n ERROR during LLM extraction:", e)
        return None
