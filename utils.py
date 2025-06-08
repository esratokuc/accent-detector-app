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
    max_bytes = 26_214_400 - 512  # 25MB - güvenli marj

    if os.path.getsize(video_path) > max_bytes:
        print("⚠️ Warning: File is large. Only the first 25MB will be analyzed.")

    with open(video_path, "rb") as f:
        file_chunk = f.read(max_bytes)

    from io import BytesIO
    partial_file = BytesIO(file_chunk)
    partial_file.name = "partial.mp4"

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

1. Summarize what the speaker is talking about in 2–4 formal sentences.
2. Analyze the speaker on the following criteria (rate 0-10):
   - Clarity of Speech
   - Diction & Pronunciation
   - Expressiveness
   - Confidence / Presence
3. Identify the **dominant emotional tone** of the speaker (e.g., serious, uplifting, calm, intense, passionate).
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

    summary_index = lines.index("Summary:") + 1
    scores_index = next(i for i, line in enumerate(lines) if line.startswith("Clarity"))

    summary = "\n".join(lines[summary_index:scores_index]).strip()

    clarity = safe_int(lines[scores_index].split(":")[-1])
    diction = safe_int(lines[scores_index + 1].split(":")[-1])
    expressiveness = safe_int(lines[scores_index + 2].split(":")[-1])
    presence = safe_int(lines[scores_index + 3].split(":")[-1])
    tone = lines[scores_index + 4].split(":", 1)[-1].strip()
    suggestion = lines[scores_index + 5].split(":", 1)[-1].strip()

    # Geriye dummy accent/confidence/explanation döndür ki unpack işlemi bozulmasın
    return (
        "N/A",         # accent
        0,             # confidence
        "N/A",         # explanation
        summary,
        clarity,
        diction,
        expressiveness,
        presence,
        tone,
        suggestion
    )

