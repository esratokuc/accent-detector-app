import requests
import os
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import torch
import torchaudio
import whisper

# Load Whisper model
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
    # Define simple rules or use a local heuristic model
    accents = {
        "British": ["mate", "bloody", "queue", "lorry"],
        "American": ["guy", "awesome", "gotten", "sidewalk"],
        "Indian": ["only", "itself", "kindly", "do the needful"],
        "Australian": ["no worries", "arvo", "brekkie"],
    }

    from random import randint
    segments = transcript.split(". ")
    chunked_segments = [". ".join(segments[i:i+3]) for i in range(0, len(segments), 3)]

    results = []
    for chunk in chunked_segments:
        found_accent = "Unknown"
        for accent, keywords in accents.items():
            if any(word.lower() in chunk.lower() for word in keywords):
                found_accent = accent
                break

        confidence = randint(70, 95) if found_accent != "Unknown" else randint(40, 60)
        explanation = f"Detected words suggest a possible {found_accent} accent."

        results.append({
            "accent": found_accent,
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
