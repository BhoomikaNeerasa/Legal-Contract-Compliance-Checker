from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# ---------------- TEXT REPORT ----------------

def generate_text_report(results, decision_text, risk_level, path, contract_name=None):
    with open(path, "w", encoding="utf-8") as f:

        # CONTRACT NAME (CENTERED, CAPS)
        if contract_name:
            title = contract_name.upper()
            f.write(title.center(60) + "\n")
            f.write("=" * 60 + "\n")

        # FINAL DECISION (BOLD STYLE USING CAPS)
        f.write("FINAL COMPLIANCE DECISION\n")
        f.write("=" * 60 + "\n")
        f.write(f"OVERALL RISK LEVEL: {risk_level}\n")
        f.write(decision_text.upper() + "\n")
        f.write("=" * 60 + "\n\n")

        # CLAUSE DETAILS
        for i, r in enumerate(results, start=1):
            f.write(f"Clause {i}\n")
            f.write(r["clause"] + "\n")
            f.write(f"Risk Level: {r['risk']}\n")
            f.write(f"Laws Violated: {', '.join(r['laws']) or 'None'}\n")
            f.write(f"Explanation: {r['explanation']}\n")
            f.write(f"Suggested Fix: {r['fix']}\n")
            f.write("-" * 60 + "\n\n")


# ---------------- PDF REPORT ----------------

def generate_pdf_report(results, decision_text, risk_level, path, contract_name=None):
    pdf = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 60

    # CONTRACT NAME (CENTERED, CAPS)
    if contract_name:
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(width / 2, y, contract_name.upper())
        y -= 25
        pdf.line(40, y, width - 40, y)
        y -= 30

    # FINAL DECISION (BOLD)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(width / 2, y, "FINAL COMPLIANCE DECISION")
    y -= 20

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawCentredString(width / 2, y, f"OVERALL RISK LEVEL: {risk_level}")
    y -= 18

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawCentredString(width / 2, y, decision_text.upper())
    y -= 30

    pdf.line(40, y, width - 40, y)
    y -= 20

    # CLAUSE DETAILS
    pdf.setFont("Helvetica", 10)

    for i, r in enumerate(results, start=1):
        lines = [
            f"Clause {i}",
            r["clause"],
            f"Risk Level: {r['risk']}",
            f"Laws Violated: {', '.join(r['laws']) or 'None'}",
            f"Explanation: {r['explanation']}",
            f"Suggested Fix: {r['fix']}",
            "-" * 60
        ]

        for line in lines:
            pdf.drawString(40, y, line[:110])
            y -= 14

            if y < 40:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = height - 40

    pdf.save()
