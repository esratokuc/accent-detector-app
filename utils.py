import os
import time
import requests
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# API anahtarlarını streamlit secrets'tan al
ASSEMBLYAI_API_KEY = st.secrets["ASSEMBLYAI_API_KEY"]

def download_video(url, filename="video.mp4"):
    """MP4 formatında videoyu indirir"""
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return filename

def send_to_assemblyai(audio_path):
    """AssemblyAI ile transkript ve konuşmacı ayrımı yapar"""
    headers = {
        "authorization": ASSEMBLYAI_API_KEY
    }

    # 1. Upload video/audio
    with open(audio_path, 'rb') as f:
        upload_res = requests.post("https://api.assemblyai.com/v2/upload", headers=headers, files={'file': f})
        audio_url = upload_res.json()['upload_url']

    # 2. Transcribe + diarization
    transcript_request = {
        "audio_url": audio_url,
        "speaker_labels": True,
        "language_code": "en_us",
        "disfluencies": False,
        "iab_categories": False,
        "auto_highlights": False,
        "filter_profanity": True
    }

    response = requests.post("https://api.assemblyai.com/v2/transcript", json=transcript_request, headers=headers)
    transcript_id = response.json()['id']

    # 3. Polling
    while True:
        polling_response = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
        status = polling_response.json()['status']
        if status == 'completed':
            return polling_response.json()
        elif status == 'error':
            raise Exception(f"Transcription failed: {polling_response.json()['error']}")
        time.sleep(5)

def analyze_accent_from_transcript(transcript_text):
    """Konuşma metninden aksan tahmini yapar (TF-IDF benzerliği ile)"""
    accents = {
        "British": "I can't go there because it's too late and I must finish my report.",
        "American": "I can't go there cause it's too late and I gotta finish my report.",
        "Indian": "I cannot go there because it's too late and I have to finish my report.",
        "Australian": "I can't go there 'cause it's too late and I have to finish my report, mate.",
        "Irish": "I can't be goin' there now, it's too late and I must finish me report.",
        "South African": "I can't go there, it's too late and I must finish my report, hey.",
        "Canadian": "I can't go there, it's too late and I have to finish my report, eh.",
        "Nigerian": "I cannot go there now because it's too late and I have to complete my report.",
        "Jamaican": "Mi can't go dere, it too late an' mi haffi finish mi report.",
        "Singaporean": "I cannot go there leh, too late already, must finish my report lah.",
        "Turkish": "I cannot go there because it's too late and I have to finish my report, you know?",
        "French": "I cannot go there because it is too late and I must finish my report, no?",
        "Spanish": "I cannot go there because it is too late and I have to finish my report, okay?",
        "German": "I cannot go there, it's too late and I must finish my report, ja?",
        "Chinese": "I cannot go there because too late already, must finish my report now.",
        "Arabic": "I cannot go there, it is too late and I have to finish my report, habibi.",
        "Russian": "I cannot go there, it’s too late and I must finish my report, da?",
        "Brazilian Portuguese": "I cannot go there because it's too late and I have to finish my report, né?",
        "Italian": "I cannot go there, it is too late and I must finish-a my report.",
        "Greek": "I cannot go there, it’s too late and I must finish my report, malaka.",
        "Korean": "I cannot go there, too late already, I have to finish my report, ya."
    }

    documents = list(accents.values()) + [transcript_text]
    vectorizer = TfidfVectorizer().fit_transform(documents)
    vectors = vectorizer.toarray()

    similarity = cosine_similarity([vectors[-1]], vectors[:-1])[0]
    best_idx = similarity.argmax()
    best_score = round(similarity[best_idx] * 100, 2)

    accent_name = list(accents.keys())[best_idx]
    return accent_name, best_score
