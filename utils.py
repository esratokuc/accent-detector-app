import requests
from openai import OpenAI
import os
from io import BytesIO

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def download_video(url, filename="video.mp4"):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filename

def transcribe_audio(video_path):
    max_bytes = 26_214_400 - 512  # Just under 25MB

    if os.path.getsize(video_path) > max_bytes:
        print("⚠️ Large file detected. Only the first 25MB will be processed.")

    with open(video_path, "rb") as f:
        file_chunk = f.read(max_bytes)

    partial_file = BytesIO(file_chunk)
    partial_file.name = "audio.mp3"

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=partial_file
    )
    return transcript.text

def analyze_accent(transcript):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"""
You are a professional speech coach and linguistic analyst.

Please perform the following tasks for the provided transcript:

1. Provide a concise summary of what the speaker is talking about. Start this section with `Summary:` on a separate line.
2. Rate the speaker from 0–10 on:
   - Clarity of Speech
   - Diction & Pronunciation
   - Expressiveness
   - Confidence / Presence
3. Identify the emotional tone of the speaker.
4. Suggest one improvement to their speaking style.

Use this exact format:
Summary:
...

Clarity: ...
Diction: ...
Expressiveness: ...
Confidence: ...
Tone: ...
Suggestion: ...
"""
            }
        ]
    )

    answer = response.choices[0].message.content.strip()
    lines = answer.splitlines()

    def safe_int(text):
        try:
            return int(text.strip())
        except:
            return 0

    summary_index = next((i for i, line in enumerate(lines) if line.strip().startswith("Summary:")), None)
    if summary_index is None:
        raise ValueError("Missing 'Summary:' section in GPT response.")

    scores_index = next((i for i, line in enumerate(lines) if line.startswith("Clarity")), None)
    if scores_index is None:
        raise ValueError("Missing score lines in GPT response.")

    summary = "\n".join(lines[summary_index + 1 : scores_index]).strip()

    clarity = safe_int(lines[scores_index].split(":")[-1])
    diction = safe_int(lines[scores_index + 1].split(":")[-1])
    expressiveness = safe_int(lines[scores_index + 2].split(":")[-1])
    presence = safe_int(lines[scores_index + 3].split(":")[-1])
    tone = lines[scores_index + 4].split(":", 1)[-1].strip()
    suggestion = lines[scores_index + 5].split(":", 1)[-1].strip()

    # filler return values for unused parts
    return (
        "N/A", 0, "N/A",
        summary,
        clarity,
        diction,
        expressiveness,
        presence,
        tone,
        suggestion
    )
