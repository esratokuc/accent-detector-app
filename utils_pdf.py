from fpdf import FPDF
import os
import smtplib
from email.message import EmailMessage

def export_results_to_pdf(analyses, full_transcript, output_file="accent_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Accent Detection Report", ln=True, align="C")
    pdf.ln(10)

    for i, res in enumerate(analyses):
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 10, f"Speaker {i+1}:", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, 
            f"Accent: {res['accent']}\n"
            f"Confidence: {res['confidence']}%\n"
            f"Explanation: {res['explanation']}\n"
            f"Transcript Segment:\n{res['segment']}\n"
            "------------------------------------------\n"
        )

    pdf.set_font("Arial", "B", size=12)
    pdf.cell(0, 10, "Full Transcript:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, full_transcript)

    pdf.output(output_file)
    return output_file

def send_email_with_pdf(recipient_email, pdf_path, sender_email, sender_password):
    msg = EmailMessage()
    msg["Subject"] = "Accent Detection Report"
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg.set_content("Please find the attached accent analysis report.")

    with open(pdf_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(pdf_path)

    msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
