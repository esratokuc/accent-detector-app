import requests
import whisper
import os

model = whisper.load_model("base")

def download_video(url, filename="video.mp4"):
    response = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    os.system(f"ffmpeg -i {filename} -ar 16000 -ac 1 audio.wav -y")
    return "audio.wav"

def transcribe_audio_whisper(audio_path="audio.wav"):
    result = model.transcribe(audio_path)
    return result["text"]

def summarize_text(text):
    from transformers import pipeline
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    summary = summarizer(text[:1024], max_length=120, min_length=30, do_sample=False)
    return summary[0]['summary_text']
