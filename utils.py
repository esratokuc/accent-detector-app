import requests
from openai import OpenAI
import os
from io import BytesIO

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def download_video(url, filename="video.mp4"):
    """Downloads a video file from a public URL and saves it locally."""
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filename

def transcribe_audio(video_path):
    """Reads the first ~25MB of the video file and sends it to Whisper API for transcription."""
    max_bytes = 26_214_400 - 512  # 25MB safe threshold

    if os.path.getsize(video_path) > max_bytes:
        print("⚠️ Warning: File is large. Only the first 25MB will be analyzed.")

    with open(video_path, "rb") as f:
        file_chunk = f.read(max_bytes)

    partial_file = BytesIO(file_chunk)
    partial_file.name = "audio.mp3"  # Safe extension for Whisper

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=partial_file
    )
    return transcript.text

def safe_int(text, default=0):
    try:
        return int(text.strip())
    except:
        return default

def analyze_accent(transcript):
    """Sends the transcript to GPT-4 and extracts multiple structured analysis outputs."""
    prompt = f"""
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
8. Then finally, describe what kind of video this is, what activity is taking place, and what the speaker's main goal seems to be. Format it as a short YouTube-style description.

Format your answer clearly with labels:
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

YouTube-style description:
...
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt.replace("{transcript}", transcript)}]
    )

    answer = response.choices[0].message.content.strip()
    lines = answer.splitlines()

    def extract_value(label):
        for line in lines:
            if line.lower().startswith(label.lower() + ":"):
                return line.split(":", 1)[-1].strip()
        return "Not available"

    def extract_block(start_label, end_label):
        start_index = next((i for i, line in enumerate(lines) if line.lower().startswith(start_label.lower())), -1)
        end_index = next((i for i, line in enumerate(lines) if line.lower().startswith(end_label.lower())), len(lines))
        if start_index == -1:
            return "Not available"
        return "\n".join(lines[start_index + 1:end_index]).strip()

    accent = extract_value("Accent")
    confidence = safe_int(extract_value("Confidence"))
    explanation = extract_value("Explanation")
    summary = extract_block("Summary:", "Clarity")
    clarity = safe_int(extract_value("Clarity"))
    diction = safe_int(extract_value("Diction"))
    expressiveness = safe_int(extract_value("Expressiveness"))
    presence = safe_int(extract_value("Confidence"))
    tone = extract_value("Tone")
    suggestion = extract_value("Suggestion")
    video_description = extract_block("YouTube-style description:", "")

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
        suggestion,
        video_description
    )
