import requests
import tempfile
import streamlit as st
from moviepy.editor import VideoFileClip
from fpdf import FPDF
from email.message import EmailMessage
import smtplib
import uuid
import openai
import assemblyai as aai

# 🔐 API Anahtarları
aai.settings.api_key = st.secrets["ASSEMBLYAI_API_KEY"]
openai.api_key = st.secrets["OPENAI_API_KEY"]

def download_video(url, output_path):
    r = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

def transcribe_audio_whisper(video_path):
    audio_path = video_path.replace(".mp4", ".wav")
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)

    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(speaker_labels=True, language_code="en")
    transcript = transcriber.transcribe(audio_path, config=config)
    return transcript

def analyze_by_unique_speakers(transcript):
    results = []
    seen_speakers = set()

    for utterance in transcript.utterances:
        speaker_id = utterance.speaker
        if speaker_id in seen_speakers:
            continue  # Aynı kişiyi tekrar analiz etme
        seen_speakers.add(speaker_id)
        segment_text = utterance.text

        prompt = f"""
You are a professional linguist and communication analyst.

For the following English transcript spoken by one person, provide:
1. The likely English accent (e.g., British, American, etc.)
2. A confidence score (0-100%) for the accent guess.
3. The speaker's emotional tone (e.g., happy, neutral, calm, excited, etc.)
4. A 2-3 sentence summary of what the speaker is talking about.

Transcript:
{segment_text}
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response['choices'][0]['message']['content']
        # Simple extraction logic
        lines = answer.strip().splitlines()
        accent = lines[0].split(":")[-1].strip()
        confidence = int(lines[1].split(":")[-1].replace("%", "").strip())
        sentiment = lines[2].split(":")[-1].strip()
        summary = lines[3].split(":", 1)[-1].strip() if lines[3].startswith("Summary:") else " ".join(lines[3:])

        results.append({
            "speaker_id": speaker_id,
            "segment": segment_text,
            "accent": accent,
            "confidence": confidence,
            "sentiment": sentiment,
            "summary": summary
        })

    return results

def export_results_to_pdf(results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Accent Detection Report", ln=True, align="C")
    pdf.ln(10)

    for r in results:
        pdf.multi_cell(0, 10, txt=f"""
👤 Speaker {r['speaker_id']}
Accent: {r['accent']}
Confidence: {r['confidence']}%
Sentiment: {r['sentiment']}
Summary: {r['summary']}

Transcript:
{r['segment']}
""")
        pdf.ln(5)

    output_path = f"accent_report_{uuid.uuid4().hex}.pdf"
    pdf.output(output_path)
    return output_path

def send_email_with_pdf(recipient_email, pdf_path):
    msg = EmailMessage()
    msg["Subject"] = "Accent Detection Report"
    msg["From"] = st.secrets["SENDER_EMAIL"]
    msg["To"] = recipient_email
    msg.set_content("Please find the attached accent analysis report.")

    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=pdf_path)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(st.secrets["SENDER_EMAIL"], st.secrets["SENDER_PASSWORD"])
        smtp.send_message(msg)
