from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import os

def generate_pdf_report(results_dict, full_transcript, output_path="accent_analysis_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="English Accent Analysis Report", ln=True, align="C")
    pdf.ln(10)

    for speaker, data in results_dict.items():
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, txt=f"{speaker}", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=f"Accent: {data['accent']}")
        pdf.multi_cell(0, 10, txt=f"Confidence: {data['confidence']}%")
        pdf.multi_cell(0, 10, txt=f"Emotion: {data['sentiment']}")
        pdf.multi_cell(0, 10, txt=f"Summary: {data['explanation']}")
        pdf.ln(5)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, txt="Full Transcript", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=full_transcript)

    pdf.output(output_path)
    return output_path

def send_report_email(to_email, pdf_path, sender_email, sender_password):
    msg = EmailMessage()
    msg['Subject'] = 'English Accent Analysis Report'
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content('Attached is your accent analysis PDF report.')

    with open(pdf_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(pdf_path))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
