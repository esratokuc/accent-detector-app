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
    max_bytes = 26_214_400 - 512  # 25MB sınırı - güvenli tampon

    if os.path.getsize(video_path) > max_bytes:
        print("⚠️ Warning: File is large. Only the first 25MB will be analyzed.")

    with open(video_path, "rb") as f:
        file_chunk = f.read(max_bytes)

    partial_file = BytesIO(file_chunk)
    partial_file.name = "audio.mp3"  # Whisper için güvenli format

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
You are an expert communication analyst.

TASKS:

1. Identify the speaker's likely English accent (e.g., British, American, Indian, etc.)
2. Give a confidence score (0-100%) for your accent guess.
3. Briefly explain why you identified this accent (1-2 sentences).
4. Summarize what the speaker is talking about in 2–4 formal sentences.
5. Analyze the speaker on the following criteria (rate 0-10):
   - Clarity of Speech
   - Diction & Pronunciation
   - Expressiveness
   - Confidence / Presence
6. Identify the **dominant emotional tone** of the speaker (e.g., serious, uplifting, calm, intense, passionate).
7. Suggest one improvement to their speaking style.

Use this exact format:

Accent: ...
Confidence: ...
Explanation: ...

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

    accent = lines[0].split(":")[-1].strip()
    confidence = int(lines[1].split(":")[-1].replace("%", "").strip())
    explanation = lines[2].split(":", 1)[-1].strip()

    summary_index = lines.index("Summary:") + 1
    scores_index = next(i for i, line in enumerate(lines) if line.startswith("Clarity"))

    summary = "\n".join(lines[summary_index:scores_index]).strip()

    clarity = int(lines[scores_index].split(":")[-1].strip())
    diction = int(lines[scores_index + 1].split(":")[-1].strip())
    expressiveness = int(lines[scores_index + 2].split(":")[-1].strip())
    presence = int(lines[scores_index + 3].split(":")[-1].strip())
    tone = lines[scores_index + 4].split(":", 1)[-1].strip()
    suggestion = lines[scores_index + 5].split(":", 1)[-1].strip()

    return (
        accent,
        confidence,
        explanation,
        summary,
        clarity,
        diction,
        expressiveness,
        presence,
        tone,
        suggestion
    )
