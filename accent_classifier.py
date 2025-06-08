import streamlit as st
from openai import OpenAI
from faster_whisper import WhisperModel

# 🔐 API anahtarı st.secrets üzerinden alınır
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Whisper modeli (daha hızlı olan faster-whisper)
model = WhisperModel("base", device="cpu", compute_type="int8")

# 📌 Aksan tahmini ve özet üretme fonksiyonu
def classify_accent(audio_path: str):
    # 1. Transkripsiyon
    segments, info = model.transcribe(audio_path)
    transcript = " ".join([segment.text for segment in segments])

    # 2. OpenAI ile analiz
    prompt = f"""Analyze the following English transcript. Determine the likely English accent (e.g., American, British, Australian), give a confidence score from 0 to 100%, and summarize the content.

Transcript:
\"\"\"
{transcript}
\"\"\"

Respond in JSON format like:
{{"accent": "British", "confidence": 85.2, "summary": "Speaker talked about their education and work."}}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    # Yanıttan JSON cevabını çek
    try:
        result = eval(response.choices[0].message.content)
    except Exception:
        result = {
            "accent": "Unknown",
            "confidence": 0,
            "summary": "Failed to analyze."
        }

    return result
