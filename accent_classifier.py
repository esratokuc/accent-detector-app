from faster_whisper import WhisperModel
from openai import OpenAI
import streamlit as st
import json

# ✅ Güvenli client bağlantısı — API key açıkça burada verilmeli çünkü Cloud'da bazen env çekmez
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Whisper modeli
model = WhisperModel("base", device="cpu")

def classify_accent(audio_path):
    segments, info = model.transcribe(audio_path)
    text = " ".join([segment.text for segment in segments])
    language = info.language

    if language != "en":
        return {
            "accent": "Non-English",
            "confidence": 0,
            "summary": f"Detected language is {language.upper()}, not English."
        }

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in English accent classification."},
                {"role": "user", "content": f"""
Given the following English transcript, determine the speaker's English accent.
Options: American, British, Australian, Indian, Other.

Then give a confidence score (0-100%) and a 1-2 sentence summary of what is being said.

Transcript:
\"{text}\"

Return your response in JSON format like:
{{"accent": "...", "confidence": ..., "summary": "..."}}.
"""}
            ],
            temperature=0.3
        )

        gpt_reply = response.choices[0].message.content
        result = json.loads(gpt_reply)
        return result

    except Exception as e:
        return {
            "accent": "Unknown",
            "confidence": 0,
            "summary": f"Error: {str(e)}"
        }
