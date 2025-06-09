import requests
import os
import time
from openai import OpenAI

# API anahtarlarını al
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_with_assemblyai(video_url):
    """
    AssemblyAI üzerinden video URL'sini çözümleyerek konuşmacı ayırımı yapılmış transkriptleri döndürür.
    """
    endpoint = "https://api.assemblyai.com/v2/transcript"
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    json = {
        "audio_url": video_url,
        "speaker_labels": True,
        "iab_categories": False,
        "entity_detection": False,
        "sentiment_analysis": False
    }

    response = requests.post(endpoint, json=json, headers=headers)
    transcript_id = response.json()["id"]

    # Transkripsiyon tamamlanana kadar bekle
    while True:
        poll = requests.get(f"{endpoint}/{transcript_id}", headers=headers).json()
        if poll["status"] == "completed":
            return poll["utterances"]
        elif poll["status"] == "error":
            raise Exception("Transcription failed:", poll["error"])
        time.sleep(5)

def analyze_with_openai(text):
    """
    OpenAI GPT-3.5 ile aksan, duygu ve özet analizi yapar.
    """
    prompt = f"""
Analyze the following English transcript and answer:
1. What is the speaker's likely English accent?
2. What is the speaker's emotional tone?
3. Write a short 1-2 sentence summary.

Text:
\"\"\"{text}\"\"\"

Respond in this format:
Accent: ...
Emotion: ...
Summary: ...
"""

    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content.strip()

def process_video_and_analyze(video_url):
    """
    Videoyu AssemblyAI ile analiz eder, her konuşmacıyı tespit eder ve OpenAI ile duygu + aksan yorumları üretir.
    """
    utterances = transcribe_with_assemblyai(video_url)

    # Konuşmacılara göre gruplama
    speakers = {}
    for u in utterances:
        spk = u["speaker"]
        if spk not in speakers:
            speakers[spk] = {"segments": [], "full_text": ""}
        speakers[spk]["segments"].append(u)
        speakers[spk]["full_text"] += " " + u["text"]

    final_results = {}
    for i, (spk, data) in enumerate(speakers.items()):
        ai_response = analyze_with_openai(data["full_text"])

        # Varsayılan değerler
        accent = emotion = explanation = "N/A"
        for line in ai_response.splitlines():
            if line.lower().startswith("accent:"):
                accent = line.split(":", 1)[1].strip()
            elif line.lower().startswith("emotion:"):
                emotion = line.split(":", 1)[1].strip()
            elif line.lower().startswith("summary:"):
                explanation = line.split(":", 1)[1].strip()

        final_results[f"Speaker {i+1}"] = {
            "accent": accent,
            "sentiment": emotion,
            "explanation": explanation,
            "segments": data["segments"]
        }

    return final_results
