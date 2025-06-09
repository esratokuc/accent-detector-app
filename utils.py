import requests
import tempfile
import os
import assemblyai as aai
from openai import OpenAI

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def download_video(url, output_path="video.mp4"):
    response = requests.get(url, stream=True)
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path

def transcribe_with_speaker_labels(video_path):
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(speaker_labels=True)
    transcript = transcriber.transcribe(video_path, config=config)
    return transcript

def group_transcript_by_speaker(transcript_obj):
    speaker_map = {}
    full_text = ""

    for utterance in transcript_obj.utterances:
        spk = f"Speaker {utterance.speaker}"
        if spk not in speaker_map:
            speaker_map[spk] = []
        segment_text = utterance.text.strip()
        speaker_map[spk].append(segment_text)
        full_text += segment_text + " "

    for speaker in speaker_map:
        speaker_map[speaker] = " ".join(speaker_map[speaker])

    return speaker_map, full_text.strip()

def analyze_with_openai(text):
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an expert linguist and psychologist. Given a text from a speaker, identify their English accent, emotional tone, and provide a brief explanation of what they're talking about."
            },
            {
                "role": "user",
                "content": f"""
TEXT: {text}

Please answer in this format:
Accent: ...
Confidence: ...%
Sentiment: ...
Explanation: ...
"""
            }
        ]
    )

    content = response.choices[0].message.content
    lines = content.splitlines()

    def extract_value(label):
        for line in lines:
            if line.lower().startswith(label.lower()):
                return line.split(":", 1)[-1].strip()
        return "Unknown"

    return {
        "accent": extract_value("Accent"),
        "confidence": extract_value("Confidence").replace("%", ""),
        "sentiment": extract_value("Sentiment"),
        "explanation": extract_value("Explanation")
    }

def process_video_and_analyze(video_url):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        video_path = download_video(video_url, tmp.name)

    transcript_obj = transcribe_with_speaker_labels(video_path)
    grouped_speakers, full_text = group_transcript_by_speaker(transcript_obj)

    results = {}
    for speaker, text in grouped_speakers.items():
        analysis = analyze_with_openai(text)
        results[speaker] = {
            "segment": text,
            **analysis
        }

    return results, full_text
