import requests
import os
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def download_video(url, filename="video.mp4"):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filename

def transcribe_audio(video_path):
    max_bytes = 25 * 1024 * 1024  # 25MB limit
    with open(video_path, "rb") as f:
        chunk = f.read(max_bytes)
    buffer = BytesIO(chunk)
    buffer.name = "audio.mp4"

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=buffer
    )
    return transcript.text

def analyze_segments(transcript):
    import textwrap

    parts = textwrap.wrap(transcript, 400, break_long_words=False)
    results = []

    for part in parts:
        prompt = f"""
You are an expert in linguistic analysis.

For the following English speech segment, determine:
1. The likely English accent (British, American, Indian, etc.)
2. The emotional tone (e.g. Neutral, Happy, Angry, Sad, etc.)
3. A short 1-2 sentence summary of the content.

Text:
{part}
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        results.append({
            "segment": part,
            "analysis": content
        })

    return results

def export_results_to_pdf(results, output_file="accent_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Accent Detection Report", ln=True, align="C")
    pdf.ln(10)

    for idx, item in enumerate(results):
        pdf.multi_cell(0, 10, txt=f"""
Segment {idx + 1}:
Text: {item['segment']}
Analysis:
{item['analysis']}
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
