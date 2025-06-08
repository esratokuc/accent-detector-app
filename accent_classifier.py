import streamlit as st
from openai import OpenAI
from faster_whisper import WhisperModel

# OpenAI client with API key from secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Whisper model for transcription
model = WhisperModel("base", device="cpu", compute_type="int8")

def classify_accent(audio_path: str):
    segments, info = model.transcribe(audio_path)
    transcript = " ".join([segment.text for segment in segments])

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

    try:
        result = eval(response.choices[0].message.content)
    except Exception:
        result = {
            "accent": "Unknown",
            "confidence": 0,
            "summary": "Failed to analyze."
        }

    return result
