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
    max_bytes = 26_214_400 - 512  # 25MB safe margin
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
    # Split the transcript into segments of approximately 150 words
    words = transcript.split()
    segments = [' '.join(words[i:i + 150]) for i in range(0, len(words), 150)]

    full_report = []
    for idx, segment in enumerate(segments):
        prompt = f"""
You are an expert linguist specialized in English accents.
For the following segment, identify:
- The likely English accent (e.g., British, American, Indian, etc.)
- A confidence score (0–100%)
- A short explanation (1–2 sentences).

Segment {idx+1}:
{segment}
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        full_report.append(response.choices[0].message.content.strip())

    return "\n\n".join(full_report)

def export_results_to_pdf(accent_report, transcript, output_file="accent_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Accent Detection Report", ln=True, align="C")
    pdf.ln(10)

    pdf.multi_cell(0, 10, txt=f"""
Accent Analysis:

{accent_report}

Transcript:
{transcript}
""")
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
