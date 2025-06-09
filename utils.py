import requests
import os
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import torch
import torchaudio
import whisper
import openai
from transformers import pipeline

# Load Whisper model
whisper_model = whisper.load_model("base")

# Load sentiment analysis model
sentiment_pipeline = pipeline("sentiment-analysis")

openai.api_key = os.getenv("OPENAI_API_KEY")

def download_video(url, filename="video.mp4"):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filename

def transcribe_audio_whisper(video_path):
    result = whisper_model.transcribe(video_path, word_timestamps=True)
    return result

def segment_speakers_and_analyze(whisper_result):
    segments = whisper_result['segments']
    processed_texts = set()
    results = []

    for segment in segments:
        text = segment['text'].strip()
        if len(text) < 10 or text in processed_texts:
            continue
        if any(x in text.lower() for x in ["laugh", "cough", "[music]", "♪"]):
            continue

        processed_texts.add(text)

        # Accent analysis (simple keyword-based for local)
        accents = {
            "British": ["mate", "bloody", "queue", "lorry"],
            "American": ["guy", "awesome", "gotten", "sidewalk"],
            "Indian": ["kindly", "do the needful"],
            "Australian": ["no worries", "arvo", "brekkie"]
        }
        found_accent = "Unknown"
        for accent, keywords in accents.items():
            if any(word.lower() in text.lower() for word in keywords):
                found_accent = accent
                break

        # GPT ile özet
        try:
            summary_prompt = f"Summarize the following statement: {text}"
            summary_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.7
            )
            explanation = summary_response['choices'][0]['message']['content'].strip()
        except:
            explanation = "Could not generate summary."

        # Sentiment analysis
        sentiment_result = sentiment_pipeline(text)[0]

        results.append({
            "accent": found_accent,
            "confidence": 85 if found_accent != "Unknown" else 50,
            "explanation": explanation,
            "sentiment": sentiment_result['label'],
            "segment": text
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
Sentiment: {res['sentiment']}
Summary: {res['explanation']}
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
