import requests
import subprocess
import openai
import os

def download_video(url, filename="video.mp4"):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filename

def extract_audio(video_path):
    audio_path = "audio.wav"
    command = f'ffmpeg -i "{video_path}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{audio_path}"'
    subprocess.run(command, shell=True, check=True)
    return audio_path

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)["text"]
    return transcript

def analyze_accent(transcript):
    prompt = f"""
You are an expert linguist specialized in English accents. Analyze the following transcript and audio context to determine:
- The likely English accent (e.g., British, American, Indian, etc.)
- Confidence score (0-100%)
- Short 1-2 sentence explanation.

Transcript:
{transcript}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response["choices"][0]["message"]["content"]
    lines = answer.strip().splitlines()
    accent = lines[0].split(":")[-1].strip()
    confidence = int(lines[1].split(":")[-1].replace("%", "").strip())
    explanation = lines[2].split(":", 1)[-1].strip()
    return accent, confidence, explanation
