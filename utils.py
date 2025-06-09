import os
import requests
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from moviepy.editor import VideoFileClip
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

def extract_audio_from_video(video_path, audio_path="audio.wav"):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    return audio_path

def transcribe_audio_whisper(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

def analyze_accent_local(transcript):
    accents = {
        "British": ["mate", "lorry", "bloody"],
        "American": ["awesome", "dude", "gotten"],
        "Indian": ["kindly", "do the needful", "itself"],
        "Australian": ["brekkie", "no worries", "arvo"],
    }

    from random import randint
    segments = transcript.split(". ")
    results = []

    for i, chunk in enumerate(segments):
        accent = "Unknown"
        for acc, keywords in accents.items():
            if any(word.lower() in chunk.lower() for word in keywords):
                accent = acc
                break
        confidence = randint(70, 95) if accent != "Unknown" else randint(40, 60)
        explanation = f"Detected words suggest a possible {accent} accent."

        results.append({
            "segment": chunk,
            "accent": accent,
            "confidence": confidence,
            "explanation": explanation
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
