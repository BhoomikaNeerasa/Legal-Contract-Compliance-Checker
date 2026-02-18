from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
import os
import json
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from durable_rule_engine import RULE_HIT_COUNTER
from llm_extractor import chat_with_llm
from contract_analyzer import analyze_contract
from report_generator import generate_text_report, generate_pdf_report
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__, template_folder="../templates")
app.secret_key = "your_secret_key_here"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "..", "reports")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}

client = MongoClient("mongodb://localhost:27017/")
db = client["compliance_checker"]
users = db["users"]
contracts = db["contracts"]
stats = db["stats"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "youremail@gmail.com"
APP_PASSWORD = "your_16_digit_app_password"


# Initialize stats if empty
if stats.count_documents({}) == 0:
    stats.insert_one({
        "total_visits": 0,
        "total_logins": 0,
        "total_uploads": 0
    })



LAST_REPORT = {}
LAST_ANALYSIS = None


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def send_otp_email(recipient_email, otp):

    subject = "Compliance Checker OTP Verification"
    body = f"""
Hello,

Your OTP for Compliance Checker is: {otp}

This OTP is valid for 5 minutes.

Regards,
Compliance Checker Team
"""

    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Email Error:", e)
        return False


# -------------------------
# PUBLIC ROUTES
# -------------------------

@app.route("/")
def home():
    stats.update_one({}, {"$inc": {"total_visits": 1}})
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")




@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = users.find_one({"email": email})

        if not user:
            return render_template("login.html",
                                   error="Email not registered")

        if not check_password_hash(user["password"], password):
            return render_template("login.html",
                                   error="Incorrect password")

        otp = str(random.randint(100000, 999999))

        session["login_otp"] = otp
        session["otp_expiry"] = time.time() + 300
        session["login_user"] = {
                "name": user["name"],
                "email": user["email"]
            }


        send_otp_email(user["email"], otp)

        return redirect("/verify-login-otp")

    return render_template("login.html")

@app.route("/verify-login-otp", methods=["GET", "POST"])
def verify_login_otp():

    if request.method == "POST":

        entered_otp = request.form["otp"]

        if time.time() > session.get("otp_expiry", 0):
            session.clear()
            return render_template(
                "verify-otp.html",
                error="OTP expired",
                email=session.get("login_user", {}).get("email")
            )

        if entered_otp == session.get("login_otp"):

            session["user"] = session["login_user"]["name"]

            stats.update_one({}, {"$inc": {"total_logins": 1}})

            session.pop("login_otp", None)
            session.pop("login_user", None)

            return redirect("/dashboard")

        else:
            return render_template(
                "verify-otp.html",
                error="Invalid OTP",
                email=session.get("login_user", {}).get("email")
            )


    return render_template(
    "verify-otp.html",
    email=session.get("login_user", {}).get("email")
    )

@app.route("/resend-login-otp")
def resend_login_otp():

    if "login_user" not in session:
        return redirect("/login")

    otp = str(random.randint(100000, 999999))

    session["login_otp"] = otp
    session["otp_expiry"] = time.time() + 300

    send_otp_email(session["login_user"]["email"], otp)

    return redirect("/verify-login-otp")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form.get("email")
        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            return render_template("register.html",
                                   error="Passwords do not match")

        if users.find_one({"email": email}):
            return render_template("register.html",
                           error="Email already registered")


        otp = str(random.randint(100000, 999999))

        session["register_otp"] = otp
        session["otp_expiry"] = time.time() + 300
        session["pending_user"] = {
            "name": name,
            "email": email,
            "password": generate_password_hash(password)
        }

        sent = send_otp_email(email, otp)

        if not sent:
            return render_template("register.html",
                                   error="OTP sending failed")

        return redirect("/verify-register-otp")

    return render_template("register.html")

@app.route("/verify-register-otp", methods=["GET", "POST"])
def verify_register_otp():

    if request.method == "POST":

        entered_otp = request.form["otp"]

        if time.time() > session.get("otp_expiry", 0):
            session.clear()
            return render_template("verify-otp.html",
                                   error="OTP expired")

        if entered_otp == session.get("register_otp"):

            users.insert_one(session["pending_user"])
            session.clear()

            return render_template("login.html",
                                   success="Registration successful. Please login.")

        else:
            return render_template("verify-otp.html",
                                   error="Invalid OTP")

    return render_template("verify-otp.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        user = users.find_one({"email": email})

        if not user:
            return render_template("forgot-password.html",
                                   error="Email not found")

        otp = str(random.randint(100000, 999999))

        session["reset_otp"] = otp
        session["reset_email"] = email
        session["otp_expiry"] = time.time() + 300

        send_otp_email(email, otp)

        return redirect("/verify-reset-otp")

    return render_template("forgot-password.html")

@app.route("/verify-reset-otp", methods=["GET", "POST"])
def verify_reset_otp():

    if request.method == "POST":

        entered_otp = request.form["otp"]
        new_password = request.form["new_password"]

        if time.time() > session.get("otp_expiry", 0):
            session.clear()
            return render_template("reset-password.html",
                                   error="OTP expired")

        if entered_otp == session.get("reset_otp"):

            users.update_one(
                {"email": session["reset_email"]},
                {"$set": {"password": generate_password_hash(new_password)}}
            )

            session.clear()

            return render_template("login.html",
                                   success="Password updated successfully.")

        else:
            return render_template("reset-password.html",
                                   error="Invalid OTP")

    return render_template("reset-password.html")

@app.route("/resend-reset-otp")
def resend_reset_otp():

    if "reset_email" not in session:
        return redirect("/forgot-password")

    otp = str(random.randint(100000, 999999))

    session["reset_otp"] = otp
    session["otp_expiry"] = time.time() + 300

    send_otp_email(session["reset_email"], otp)

    return redirect("/verify-reset-otp")


# -------------------------
# PROTECTED ROUTES
# -------------------------

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


@app.route("/upload")
def upload_page():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("upload.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


@app.route("/navbar-auth.html")
def navbar():
    return render_template("navbar-auth.html")


# -------------------------
# ANALYSIS + CHAT (UNCHANGED LOGIC)
# -------------------------

@app.route("/analyze", methods=["POST"])
def analyze():
    global LAST_ANALYSIS

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if "contract" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["contract"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    results, decision_text, risk_level, full_text, metadata = analyze_contract(upload_path)

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

    generate_text_report(results, decision_text, risk_level, txt_path, base_name)
    generate_pdf_report(results, decision_text, risk_level, pdf_path, base_name)

    LAST_REPORT["txt"] = txt_path
    LAST_REPORT["pdf"] = pdf_path

    contracts.insert_one({
        "user": session["user"],
        "filename": filename,
        "analysis": results,
        "decision": decision_text,
        "risk": risk_level
    })
    stats.update_one({}, {"$inc": {"total_uploads": 1}})

    return jsonify({
        "filename": filename,
        "decision": decision_text,
        "analysis": results
    })


@app.route("/chat", methods=["POST"])
def chat():
    # 🔐 Session Protection (NEW)
    if "user" not in session:
        return jsonify({"answer": "Unauthorized access. Please login."})

    # 🔹 Keep original behavior
    if not LAST_ANALYSIS:
        return jsonify({"answer": "Please analyze a contract first."})

    question = request.json.get("question", "").strip()
    if not question:
        return jsonify({"answer": "Please ask a valid question."})

    # 🔹 KEEP YOUR ORIGINAL CONTEXT BUILDING
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

    # 🔥 YOUR ORIGINAL FULL PROMPT (UNCHANGED)
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


if __name__ == "__main__":
    app.run(debug=True,use_reloader=False)

