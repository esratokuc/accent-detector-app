import streamlit as st
from utils import download_video, extract_audio, transcribe_audio, analyze_accent
import os
import uuid

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (via URL)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and processing video..."):
        try:
            # Benzersiz bir video adı oluştur (boşluk, sembol vs. sorun olmasın diye)
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"

            # Videoyu indir
            video_path = download_video(video_url, filename=video_filename)

            # Sesi çıkar
            audio_path = extract_audio(video_path)

            # Transkript ve aksan analizi
            transcript = transcribe_audio(audio_path)
            accent, confidence, explanation = analyze_accent(transcript)

            # Sonuçları göster
            st.success("✅ Analysis Complete!")
            st.markdown(f"**🗣️ Detected Accent:** `{accent}`")
            st.markdown(f"**📊 Confidence Score:** `{confidence}%`")
            st.markdown(f"**🧠 Explanation:** _{explanation}_")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")
