import requests
import torch
import tempfile
import pdfkit
from transformers import pipeline
from moviepy.editor import VideoFileClip
import assemblyai as aai
import uuid

# Configure AssemblyAI API
aai.settings.api_key = "YOUR_ASSEMBLYAI_API_KEY"

# Sentiment & summarizer pipelines
sentiment_analyzer = pipeline("sentiment-analysis")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def download_video(url, output_path):
    r = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

def transcribe_audio_whisper(video_path):
    audio_path = video_path.replace(".mp4", ".wav")
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)

    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(speaker_labels=True, language_code="en")
    transcript = transcriber.transcribe(audio_path, config=config)
    return transcript

def segment_speakers_and_analyze(transcript):
    results = []
    seen_speakers = set()

    for utterance in transcript.utterances:
        speaker_id = utterance.speaker
        if speaker_id in seen_speakers:
            continue  # Her konuşmacıyı sadece bir kere analiz et
        seen_speakers.add(speaker_id)

        segment_text = utterance.text

        # Aksan tespiti örnek model yerine rastgele
        accent = "British" if "London" in segment_text or "gin" in segment_text else "American"
        confidence = round(torch.rand(1).item() * 100, 2)

        sentiment = sentiment_analyzer(segment_text)[0]['label']
        summary = summarizer(segment_text, max_length=60, min_length=10, do_sample=False)[0]['summary_text']

        results.append({
            "speaker_id": speaker_id,
            "segment": segment_text,
            "accent": accent,
            "confidence": confidence,
            "sentiment": sentiment,
            "summary": summary
        })

    return results

def export_results_to_pdf(results):
    html = "<h1>Accent Analysis Report</h1>"
    for r in results:
        html += f"""
        <h2>Speaker {r['speaker_id']}</h2>
        <ul>
            <li><strong>Accent:</strong> {r['accent']}</li>
            <li><strong>Confidence:</strong> {r['confidence']}%</li>
            <li><strong>Sentiment:</strong> {r['sentiment']}</li>
            <li><strong>Summary:</strong> {r['summary']}</li>
            <li><strong>Transcript:</strong> {r['segment']}</li>
        </ul>
        <hr>
        """
    output_path = f"accent_report_{uuid.uuid4().hex}.pdf"
    pdfkit.from_string(html, output_path)
    return output_path
