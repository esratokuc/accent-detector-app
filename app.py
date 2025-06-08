import streamlit as st
import os
from audio_utils import extract_audio
from accent_classifier import classify_accent
import tempfile

st.set_page_config(page_title="Accent Detector", page_icon="🎙️")
st.title("🎙️ English Accent Detector")

st.markdown("Upload a public video URL or .mp4 file to detect spoken English accent.")

# 1. Video Yükleme
video_file = st.file_uploader("Upload an MP4 video", type=["mp4"])
if video_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
        tmp_video.write(video_file.read())
        video_path = tmp_video.name

    # 2. Videodan sesi çıkar
    with st.spinner("🔊 Extracting audio..."):
        audio_path = extract_audio(video_path)

    # 3. Aksan Analizi
    with st.spinner("🧠 Analyzing accent..."):
        result = classify_accent(audio_path)

    # 4. Sonuç Göster
    st.subheader("🎯 Result")
    st.write(f"**Accent:** {result.get('accent', 'Unknown')}")
    st.write(f"**Confidence:** {result.get('confidence', 0)}%")
    st.write(f"**Summary:** {result.get('summary', 'No summary available.')}")

    # Temizlik
    os.remove(video_path)
    os.remove(audio_path)
