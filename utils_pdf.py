from fpdf import FPDF
import os
import smtplib
from email.message import EmailMessage

def generate_pdf_report(results, full_text, output_path="accent_analysis_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Accent Analysis Report", ln=True, align="C")
    pdf.ln(10)

    for item in results:
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt=f"Speaker: {item['speaker']}", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, txt=f"Accent: {item['accent']}")
        pdf.multi_cell(0, 10, txt=f"Confidence: {item['confidence']}%")
        pdf.multi_cell(0, 10, txt=f"Sentiment: {item['sentiment']}")
        pdf.multi_cell(0, 10, txt=f"Summary: {item['explanation']}")
        pdf.ln(5)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Full Transcript", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, txt=full_text)

    pdf.output(output_path)
    return output_path

def send_report_email(to_email, pdf_path):
    msg = EmailMessage()
    msg["Subject"] = "Your Accent Analysis Report"
    msg["From"] = os.getenv("SENDER_EMAIL")
    msg["To"] = to_email
    msg.set_content("Please find attached your PDF report.")

    with open(pdf_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(pdf_path)

    msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD"))
        smtp.send_message(msg)
