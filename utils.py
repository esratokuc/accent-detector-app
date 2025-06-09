import requests
import time
import openai
import os

# Set your API keys
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def upload_to_assemblyai(audio_url):
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    json = {"audio_url": audio_url, "speaker_labels": True}
    response = requests.post("https://api.assemblyai.com/v2/transcript", json=json, headers=headers)
    transcript_id = response.json()["id"]

    # Poll until done
    while True:
        polling = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers).json()
        if polling["status"] == "completed":
            return polling["utterances"]
        elif polling["status"] == "error":
            raise Exception("Transcription failed:", polling["error"])
        time.sleep(5)

def openai_analyze(text):
    prompt = f"""
Given the following spoken text, detect:
1. English accent (e.g., British, American, Australian)
2. The emotion (e.g., happy, neutral, nostalgic)
3. A 1-2 sentence summary

Text:
\"\"\"{text}\"\"\"

Respond in this format:

Accent: ...
Emotion: ...
Summary: ...
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def process_video_and_analyze(video_url):
    # Step 1: Transcribe and detect speakers
    utterances = upload_to_assemblyai(video_url)

    speaker_data = {}
    for u in utterances:
        speaker = u["speaker"]
        text = u["text"]
        if speaker not in speaker_data:
            speaker_data[speaker] = {"full_text": [], "segments": []}
        speaker_data[speaker]["full_text"].append(text)
        speaker_data[speaker]["segments"].append(text)

    # Step 2: Run OpenAI for each speaker's full text
    final_results = {}
    for speaker, data in speaker_data.items():
        joined_text = " ".join(data["full_text"])
        result_text = openai_analyze(joined_text)

        parsed = {}
        for line in result_text.strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                parsed[key.strip().lower()] = val.strip()

        final_results[speaker] = {
            "accent": parsed.get("accent", "N/A"),
            "emotion": parsed.get("emotion", "N/A"),
            "summary": parsed.get("summary", "N/A"),
            "segments": data["segments"]
        }

    return final_results
