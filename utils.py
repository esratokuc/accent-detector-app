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
    max_bytes = 26_214_400 - 512  # 25MB güvenli sınır
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

def split_transcript_by_segments(transcript, segment_length=150):
    words = transcript.split()
    segments = [' '.join(words[i:i + segment_length]) for i in range(0, len(words), segment_length)]
    return segments

def analyze_accent(transcript):
    segments = split_transcript_by_segments(transcript)
    results = []

    for idx, seg in enumerate(segments):
        prompt = f"""
You are an expert linguist specialized in English accents. Please analyze the following segment of a conversation.

Provide:
- Likely English accent (e.g., British, American, Indian, etc.)
- Confidence score (0-100%)
- One-sentence explanation (reasoning)

Transcript Segment:
\"\"\"{seg}\"\"\"
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content.strip()
            lines = answer.splitlines()

            def get_value(label):
                line = next((l for l in lines if l.lower().startswith(label.lower())), None)
                return line.split(":", 1)[-1].strip() if line else "Not available"

            accent = get_value("Accent")
            confidence = get_value("Confidence")
            explanation = get_value("Explanation")

            results.append({
                "segment": seg,
                "accent": accent,
                "confidence": confidence,
                "explanation": explanation
            })

        except Exception as e:
            results.append({
                "segment": seg,
                "accent": "Error",
                "confidence": "0%",
                "explanation": f"Failed to analyze segment: {str(e)}"
            })

    return results

def export_results_to_pdf(results, transcript, output_file="accent_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Accent Detection Report", ln=True, align="C")
    pdf.ln(10)

    for i, result in enumerate(results):
        pdf.set_font("Arial", style="B", size=11)
        pdf.multi_cell(0, 8, txt=f"[Segment {i+1}]")
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, txt=f"Accent: {result['accent']}\nConfidence: {result['confidence']}\nExplanation: {result['explanation']}")
        pdf.multi_cell(0, 8, txt=f"Transcript: {result['segment']}")
        pdf.ln(5)

    pdf.output(output_file)
    return output_file

def send_email_with_pdf(recipient_email, pdf_path, sender_email, sender_password):
    msg = EmailMessage()
    msg["Subject"] = "Accent Detection Report"
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg.set_content("Please find attached the PDF report of the accent analysis.")

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(pdf_path)
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
