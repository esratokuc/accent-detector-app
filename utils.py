import os
import requests
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import whisper
from transformers import pipeline

# Placeholder for improved accent classifier (multi-class accent detection)
accent_classifier = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")

ACCEPTED_ACCENTS = [
    "American", "British", "Indian", "Australian", "Irish", "Canadian", "South African"
]

def download_video(url, filename="video.mp4"):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filename

def transcribe_audio_whisper(video_path):
    model = whisper.load_model("base")  # Model yüklemesi fonksiyon içinde
    result = model.transcribe(video_path)
    return result["text"]

def analyze_accent_local(transcript):
    # Naive segmentation for demonstration
    segments = transcript.split(". ")
    chunked_segments = [". ".join(segments[i:i+3]) for i in range(0, len(segments), 3)]

    results = []
    for chunk in chunked_segments:
        detected = accent_classifier(chunk)[0]
        label = detected["label"].strip()
        score = round(detected["score"] * 100)

        accent = next((acc for acc in ACCEPTED_ACCENTS if acc.lower() in label.lower()), "Other")
        explanation = f"This segment appears to reflect a {accent} accent based on language style and tone."

        results.append({
            "accent": accent,
            "confidence": score,
            "explanation": explanation,
            "segment": chunk
        })

    return results

def export_results_to_pdf(results, output_file="accent_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Accent Detection Report", ln=True, align="C")
    pdf.ln(10)

    for idx, res in enumerate(results):
        pdf.multi_cell(0, 10, txt=f"""
Segment {idx + 1}:
Accent: {res['accent']}
Confidence Score: {res['confidence']}%
Explanation: {res['explanation']}
Transcript: {res['segment']}
""")
        pdf.ln(5)

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
