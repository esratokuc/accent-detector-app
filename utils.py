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
    max_bytes = 26_214_400 - 512  # 25MB - safety margin

    if os.path.getsize(video_path) > max_bytes:
        print("⚠️ Warning: File is large. Only the first 25MB will be analyzed.")

    with open(video_path, "rb") as f:
        file_chunk = f.read(max_bytes)

    partial_file = BytesIO(file_chunk)
    partial_file.name = "partial.mp4"

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=partial_file
    )
    return transcript.text

def split_transcript_by_segments(transcript, segment_length=150):
    # Split transcript into segments of ~segment_length words
    words = transcript.split()
    segments = [' '.join(words[i:i + segment_length]) for i in range(0, len(words), segment_length)]
    return segments

def analyze_accent(transcript):
    segments = split_transcript_by_segments(transcript)
    results = []

    for segment in segments:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"""
You are an expert linguist specialized in English accents. Analyze only verbal communication (ignore laughter or non-verbal sounds).

Determine:
- The likely English accent of the speaker (e.g., British, American, Indian, etc.)
- Confidence score (0-100%)
- Short 1-2 sentence explanation of the speech.

Segment:
{segment}
"""
                }
            ]
        )

        answer = response.choices[0].message.content
        lines = answer.strip().splitlines()
        try:
            accent = lines[0].split(":")[-1].strip()
            confidence = int(lines[1].split(":")[-1].replace("%", "").strip())
            explanation = lines[2].split(":", 1)[-1].strip()
            results.append((accent, confidence, explanation))
        except:
            results.append(("Unknown", 0, "Parsing error or unclear segment."))

    return results
