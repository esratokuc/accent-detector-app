import requests
from openai import OpenAI
import os
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def download_video(url, filename="video.mp4"):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filename

def transcribe_audio(video_path):
    max_bytes = 26_214_400 - 512  # 25MB - güvenli marj

    if os.path.getsize(video_path) > max_bytes:
        print("⚠️ Warning: File is large. Only the first 25MB will be analyzed.")

    with open(video_path, "rb") as f:
        file_chunk = f.read(max_bytes)

    partial_file = BytesIO(file_chunk)
    partial_file.name = "partial.mp4"

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=partial_file
    )
    return transcript.text

def analyze_accent(transcript):
    # Split transcript into segments by speaker turns or long pauses (naive split)
    segments = transcript.split(". ")  # Rough segmentation, better with diarization
    chunked_segments = [". ".join(segments[i:i+3]) for i in range(0, len(segments), 3)]

    results = []
    for chunk in chunked_segments:
        prompt = f"""
You are an expert linguist specialized in English accents. Analyze the following transcript to determine:
- The likely English accent (e.g., British, American, Indian, etc.)
- Confidence score (0-100%)
- Short 2-3 sentence explanation of the content

Only analyze meaningful speech. Ignore irrelevant sounds like laughter, filler words, or noise.

Transcript:
{chunk}
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content
        lines = answer.strip().splitlines()
        try:
            accent = lines[0].split(":")[-1].strip()
            confidence = int(lines[1].split(":")[-1].replace("%", "").strip())
            explanation = lines[2].split(":", 1)[-1].strip()
        except:
            accent = "N/A"
            confidence = 0
            explanation = "Parsing error."

        results.append({
            "accent": accent,
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
