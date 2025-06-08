from faster_whisper import WhisperModel
from openai import OpenAI
import streamlit as st
import json

# OpenAI client (yeni sürüm uyumlu)
client = OpenAI.from_api_key(st.secrets["OPENAI_API_KEY"])

# Whisper modeli (CPU için base modeli yeterli)
model = WhisperModel("base", device="cpu")

def classify_accent(audio_path):
    # 1. Ses dosyasından metni çıkar
    segments, info = model.transcribe(audio_path)
    text = " ".join([segment.text for segment in segments])
    language = info.language

    # 2. İngilizce değilse bildirim yap
    if language != "en":
        return {
            "accent": "Non-English",
            "confidence": 0,
            "summary": f"Detected language is {language.upper()}, not English."
        }

    # 3. OpenAI Chat API ile aksan analizi
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in English accent classification and speech analysis."
                },
                {
                    "role": "user",
                    "content": f"""
Given the following English transcript, determine the speaker's English accent.
Options: American, British, Australian, Indian, Other.

Then give:
- A confidence score (0-100%)
- A 1-2 sentence summary of what is being said.

Transcript:
\"{text}\"

Return your response in JSON format like:
{{
  "accent": "...",
  "confidence": ...,
  "summary": "..."
}}
"""
                }
            ],
            temperature=0.3
        )

        reply = response.choices[0].message.content
        result = json.loads(reply)
        return result

    except Exception as e:
        return {
            "accent": "Error",
            "confidence": 0,
            "summary": f"Failed to analyze due to: {str(e)}"
        }
