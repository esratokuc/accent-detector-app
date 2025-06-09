from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import os

def export_results_to_pdf(results, output_path="accent_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Accent & Emotion Report", ln=True, align="C")
    pdf.ln(10)

    # Speaker summary
    for spk, data in results.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"{spk}", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, txt=f"Accent: {data['accent']}\nSentiment: {data['sentiment']}\nSummary: {data['explanation']}\n")
        pdf.ln(5)

    # Full transcript
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Full Transcript", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.ln(5)

    for spk, data in results.items():
        for seg in data["segments"]:
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            text = seg["text"]
            time_range = f"[{start / 1000:.2f}s - {end / 1000:.2f}s]"
            pdf.multi_cell(0, 10, txt=f"{time_range} {spk}: {text}")
            pdf.ln(2)

    pdf.output(output_path)
    return output_path

def send_email_with_attachment(to_email, file_path, from_email, app_password):
    msg = EmailMessage()
    msg["Subject"] = "Accent Analysis Report"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content("Please find the attached accent analysis report.")

    with open(file_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="accent_report.pdf")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_email, app_password)
        smtp.send_message(msg)
