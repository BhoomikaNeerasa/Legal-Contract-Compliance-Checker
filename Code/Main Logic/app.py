from flask import Flask, request, jsonify, render_template, send_file
import os
import json
from werkzeug.utils import secure_filename
from pymongo import MongoClient

from llm_extractor import chat_with_llm
from contract_analyzer import analyze_contract
from report_generator import generate_text_report, generate_pdf_report

app = Flask(__name__, template_folder="../templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "..", "reports")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}

client = MongoClient("mongodb://localhost:27017/")
db = client["compliance_checker"]
contracts = db["contracts"]

LAST_REPORT = {}
LAST_ANALYSIS = None


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def upload_page():
    return render_template("upload.html")


@app.route("/navbar-auth.html")
def navbar():
    return render_template("navbar-auth.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    global LAST_ANALYSIS

    if "contract" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["contract"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    #  UPDATED RECEIVE
    results, decision_text, risk_level, full_text, metadata = analyze_contract(upload_path)

    #  UPDATED STORE
    LAST_ANALYSIS = {
        "filename": filename,
        "decision": decision_text,
        "risk": risk_level,
        "clauses": results,
        "full_text": full_text,
        "metadata": metadata
    }

    base_name = os.path.splitext(filename)[0]
    txt_path = os.path.join(REPORT_FOLDER, f"{base_name}_report.txt")
    pdf_path = os.path.join(REPORT_FOLDER, f"{base_name}_report.pdf")

    generate_text_report(
        results=results,
        decision_text=decision_text,
        risk_level=risk_level,
        path=txt_path,
        contract_name=filename
    )

    generate_pdf_report(
        results=results,
        decision_text=decision_text,
        risk_level=risk_level,
        path=pdf_path,
        contract_name=filename
    )

    LAST_REPORT["txt"] = txt_path
    LAST_REPORT["pdf"] = pdf_path

    contracts.insert_one({
        "filename": filename,
        "analysis": results,
        "final_decision": decision_text,
        "risk_level": risk_level
    })

    return jsonify({
        "filename": filename,
        "decision": decision_text,
        "analysis": results
    })


@app.route("/chat", methods=["POST"])
def chat():
    if not LAST_ANALYSIS:
        return jsonify({"answer": "Please analyze a contract first."})

    question = request.json.get("question", "").strip()
    if not question:
        return jsonify({"answer": "Please ask a valid question."})

    chat_context = {
    "contract_type": LAST_ANALYSIS["metadata"]["contract_type"],
    "decision": LAST_ANALYSIS["decision"],
    "risk": LAST_ANALYSIS["risk"],
    "violations": [
        {
            "risk": c["risk"],
            "laws": c["laws"],
            "explanation": c["explanation"]
        }
        for c in LAST_ANALYSIS["clauses"]
        if c["risk"] != "Safe"
    ]
}
    context = json.dumps(chat_context, indent=2)


    prompt = f"""
You are an intelligent legal contract assistant.

You help users understand legal contracts and agreements including:
- Employment agreements
- Partnership agreements
- Sponsorship agreements
- Rental and lease agreements
- General commercial contracts

You are given:
1. The analyzed contract data (clauses, risks, laws, explanations)
2. The final risk decision of the contract
3. The full contract text and metadata (if available)

PRIORITY RULES (STRICT):
1. If the user asks whether the contract is safe to sign:
   - Use the final decision (SAFE / CONCERNING / HIGH RISK)
   - Explain briefly why.

2. If the user asks about laws violated:
   - If SAFE → say no laws are violated
   - If CONCERNING / HIGH RISK → list the laws from analysis and explain them

3. If the answer exists in the contract or analysis, use it.

4. If the contract does NOT explicitly specify something:
   - First check if it can be reasonably inferred from:
     • contract type
     • roles (Employer/Employee, Client/Developer, etc.)
   - If inferred, say: "This appears to be…"
   - Otherwise say: "The contract does not specify this."

5. If the user asks a general legal question (not contract-specific),
   explain using general legal principles.

6. NEVER invent clauses, parties, or obligations.

7. If the user asks:
   - "Who is I / you / we?"
   - "What type of agreement is this?"
   - "What is the work to be done?"
   You may infer from contract structure, clearly stating it is an interpretation.

8. If the user says thanks / ok / cool / got it:
   → Respond politely and naturally
   → Do NOT mention the contract.

Contract Analysis Data:
{context}

User Question:
{question}

Answer clearly, conversationally, and like a real legal assistant.
"""


    answer = chat_with_llm(prompt)
    return jsonify({"answer": answer})


@app.route("/download/text")
def download_text():
    path = LAST_REPORT.get("txt")
    if not path or not os.path.exists(path):
        return "Text report not found", 404
    return send_file(path, as_attachment=True)


@app.route("/download/pdf")
def download_pdf():
    path = LAST_REPORT.get("pdf")
    if not path or not os.path.exists(path):
        return "PDF report not found", 404
    return send_file(path, as_attachment=True)


@app.route("/logout")
def logout():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=False)
