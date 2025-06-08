import whisper
from langdetect import detect
import random

model = whisper.load_model("base")

def classify_accent(audio_path):
    result = model.transcribe(audio_path)
    text = result["text"]

    if detect(text) != "en":
        return {
            "accent": "Non-English",
            "confidence": 0,
            "summary": "Detected language is not English."
        }

    # Fake accent classification (you can replace with real model or heuristic)
    possible_accents = ["British", "American", "Australian"]
    selected = random.choice(possible_accents)
    confidence = round(random.uniform(70, 99), 2)

    return {
        "accent": selected,
        "confidence": confidence,
        "summary": f"Likely a {selected} accent with {confidence}% confidence."
    }
