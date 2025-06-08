from faster_whisper import WhisperModel
import openai
import os

# Whisper model (transcription)
model = WhisperModel("base", device="cpu")

# GPT için anahtar (gizli şekilde ayarlayın)
openai.api_key = os.getenv("OPENAI_API_KEY")

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

    # Aksan ve özet analizi için GPT'ye gönder
    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in speech analysis."},
            {"role": "user", "content": f"""
Given the following English transcript, determine the speaker's English accent.
Options: American, British, Australian, Indian, Other.

Then give a confidence score (0-100%) and a 1-2 sentence summary of what is being said.

Transcript:
\"{text}\"

Return your response in JSON format like:
{{"accent": "...", "confidence": ..., "summary": "..."}}.
"""}
        ]
    )

    import json
    try:
        response_text = gpt_response['choices'][0]['message']['content']
        result = json.loads(response_text)
        return result
    except Exception as e:
        return {
            "accent": "Unknown",
            "confidence": 0,
            "summary": f"Could not parse GPT response. {e}"
        }
