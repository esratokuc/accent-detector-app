import requests
import os
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from openai import OpenAI
from transformers import pipeline

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
sentiment_pipeline = pipeline("sentiment-analysis")

def download_video(url, filename="video.mp4"):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filename

def transcribe_audio(video_path):
    max_bytes = 26_214_400 - 512

    if os.path.getsize(video_path) > max_bytes:
        print("⚠️ File is large. Only the first 25MB will be analyzed.")

    with open(video_path, "rb") as f:
        file_chunk = f.read(max_bytes)

    partial_file = BytesIO(file_chunk)
    partial_file.name = "partial.mp4"

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=partial_file,
        response_format="verbose_json",
        timestamp_granularities=["segment"]
    )
    return transcript

def analyze_accent_segments(transcription_result):
    processed_texts = set()
    results = []

    for segment in transcription_result['segments']:
        text = segment['text'].strip()
        if len(text) < 10 or text.lower() in processed_texts:
            continue
        if any(x in text.lower() for x in ["laugh", "cough", "music", "[", "♪", "…"]):
            continue
        processed_texts.add(text.lower())

        # OpenAI GPT ile analiz
        prompt = f"""
You are an expert linguist. For the following English sentence, determine:
- The likely English accent (British, American, Indian, Australian, etc.)
- Confidence score (0-100%)
- Summary of what is being said (2 sentence)
Transcript:
{text}
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        reply = response.choices[0].message.content.strip().splitlines()

        try:
            accent = reply[0].split(":")[-1].strip()
            confidence = int(reply[1].split(":")[-1].replace("%", "").strip())
            explanation = reply[2].split(":", 1)[-1].strip()
        except:
            accent = "Unknown"
            confidence = 50
            explanation = "Summary not available"

        sentiment = sentiment_pipeline(text)[0]['label']

        results.append({
            "segment": text,
            "accent": accent,
            "confidence": confidence,
            "explanation": explanation,
            "sentiment": sentiment
        })

    return results

def export_results_to_pdf(segments, output_file="accent_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Accent Detection Report", ln=True, align="C")
    pdf.ln(10)

    for idx, res in enumerate(segments):
        pdf.multi_cell(0, 10, txt=f"""
Segment {idx + 1}:
Accent: {res['accent']}
Confidence Score: {res['confidence']}%
Sentiment: {res['sentiment']}
Summary: {res['explanation']}
Transcript: {res['segment']}
""")
        pdf.ln(3)

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
