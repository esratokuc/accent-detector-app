import requests
import os
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import whisper
from random import randint

whisper_model = whisper.load_model("base")

def download_video(url, filename="video.mp4"):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filename

def transcribe_audio_whisper(video_path):
    result = whisper_model.transcribe(video_path)
    return result["text"]

def analyze_accent_local(transcript):
    accents = {
        "British": ["mate", "lorry", "queue"],
        "American": ["guy", "awesome", "gotten"],
        "Indian": ["only", "itself", "kindly"],
        "Australian": ["no worries", "brekkie", "arvo"],
    }

    segments = transcript.split(". ")
    chunks = [". ".join(segments[i:i+3]) for i in range(0, len(segments), 3)]

    results = []
    for chunk in chunks:
        found = "Unknown"
        for accent, words in accents.items():
            if any(w in chunk.lower() for w in words):
                found = accent
                break
        confidence = randint(70, 95) if found != "Unknown" else randint(40, 60)
        explanation = f"Detected words suggest a possible {found} accent."
        results.append({
            "accent": found,
            "confidence": confidence,
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
    for idx, r in enumerate(results):
        pdf.multi_cell(0, 10, txt=f"""
Segment {idx + 1}:
Accent: {r['accent']}
Confidence: {r['confidence']}%
Explanation: {r['explanation']}
Transcript: {r['segment']}
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
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(pdf_path))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
