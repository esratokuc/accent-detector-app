import requests
from openai import OpenAI
from pydub import AudioSegment
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def download_video(url, filename="video.mp4"):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filename

def transcribe_audio(video_path):
    # Uyarı ver: dosya boyutu çok büyükse
    if os.path.getsize(video_path) > 25_000_000:
        print("⚠️ Warning: File is large. Only first 5 minutes will be analyzed.")

    # Videodan sesi yükle
    audio = AudioSegment.from_file(video_path)

    # İlk 5 dakikayı al (300.000 ms)
    max_duration_ms = 5 * 60 * 1000
    short_audio = audio[:max_duration_ms]

    # Geçici dosyaya kaydet
    temp_path = "short_audio.wav"
    short_audio.export(temp_path, format="wav")

    # OpenAI Whisper ile transkript
    with open(temp_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return transcript.text

def analyze_accent(transcript):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"""
You are an expert linguist specialized in English accents. Analyze the following transcript and audio context to determine:
- The likely English accent (e.g., British, American, Indian, etc.)
- Confidence score (0-100%)
- Short 1-2 sentence explanation.

Transcript:
{transcript}
"""
            }
        ]
    )
    answer = response.choices[0].message.content
    lines = answer.strip().splitlines()
    accent = lines[0].split(":")[-1].strip()
    confidence = int(lines[1].split(":")[-1].replace("%", "").strip())
    explanation = lines[2].split(":", 1)[-1].strip()
    return accent, confidence, explanation
