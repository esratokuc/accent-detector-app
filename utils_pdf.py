from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import os

def generate_pdf_report(results, full_text, output_path="accent_analysis_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="English Accent Analysis Report", ln=True, align="C")
    pdf.ln(10)

    for idx, item in enumerate(results, 1):
        segment = item["segment"]
        accent = item["accent"]
        confidence = item["confidence"]
        explanation = item["explanation"]
        sentiment = item["sentiment"]

        def safe(text):
            return text.encode('latin-1', 'replace').decode('latin-1')

        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 10, txt=f"🧩 Segment {idx}:", ln=True)
        pdf.set_font("Arial", size=12)

        pdf.multi_cell(0, 10, txt=safe(f"- Accent: {accent}"))
        pdf.multi_cell(0, 10, txt=safe(f"- Confidence: {confidence}%"))
        pdf.multi_cell(0, 10, txt=safe(f"- Sentiment: {sentiment}"))
        pdf.multi_cell(0, 10, txt=safe(f"- Explanation: {explanation}"))
        pdf.multi_cell(0, 10, txt=safe(f"- Segment Text: {segment}"))
        pdf.ln(5)

    # Full transcript at the end
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, txt="🗨️ Full Transcript", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=safe(full_text))

    pdf.output(output_path)
    return output_path


def send_report_email(receiver_email, pdf_path):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    msg = EmailMessage()
    msg["Subject"] = "Your English Accent Analysis Report"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Please find your accent analysis report attached.")

    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
        msg.add_attachment(pdf_data, maintype="application", subtype="pdf", filename="accent_report.pdf")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
