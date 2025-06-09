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
    max_bytes = 26_214_400 - 512  # 25MB safety margin

    if os.path.getsize(video_path) > max_bytes:
        print("⚠️ Warning: File is large. Only the first 25MB will be analyzed.")

    with open(video_path, "rb") as f:
        file_chunk = f.read(max_bytes)

    partial_file = BytesIO(file_chunk)
    partial_file.name = "audio.mp3"  # Safe format for Whisper

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=partial_file
    )
    return transcript.text

def analyze_accent(transcript):
    """Analyze transcript for accent, clarity, tone, and summary"""
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
6. Suggest a 1-line video description.
7. Predict the speaker's emotional tone (e.g., calm, energetic, anxious).

Use this exact format:

Accent: ...
Accent Score: ...
Accent Explanation: ...

Summary:
...

Clarity: ...
Diction: ...
Expressiveness: ...
Video Description: ...
Tone: ...
"""
            }
        ]
    )

    answer = response.choices[0].message.content.strip()
    lines = answer.splitlines()

    def get_value(label):
        line = next((l for l in lines if l.startswith(label)), None)
        return line.split(":", 1)[-1].strip() if line else "Not available"

    def safe_int(text):
        try:
            return int(text)
        except:
            return "Not available"

    accent = get_value("Accent")
    confidence = safe_int(get_value("Accent Score").replace("%", ""))
    explanation = get_value("Accent Explanation")

    try:
        summary_start = lines.index("Summary:") + 1
        scores_start = next(i for i, l in enumerate(lines) if l.startswith("Clarity:"))
        summary = "\n".join(lines[summary_start:scores_start]).strip()
    except:
        summary = "Not available"

    clarity = safe_int(get_value("Clarity"))
    diction = safe_int(get_value("Diction"))
    expressiveness = safe_int(get_value("Expressiveness"))
    video_description = get_value("Video Description")
    tone = get_value("Tone")

    return (
        accent,
        confidence,
        explanation,
        summary,
        clarity,
        diction,
        expressiveness,
        video_description,
        tone
    )
