import streamlit as st
from utils import (
    download_video,
    transcribe_audio,
    analyze_accent
)
import uuid

st.set_page_config(page_title="Video İçerik Özeti", layout="centered")
st.title("🧠 Video İçeriği ve Konuşma Özeti")

video_url = st.text_input("🎥 Video linkini buraya yapıştırın (MP4 formatında):")

if st.button("📊 Analiz Et") and video_url:
    with st.spinner("Video indiriliyor ve analiz ediliyor..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            transcript = transcribe_audio(video_path)

            (
                accent,
                confidence,
                explanation,
                summary,
                clarity,
                diction,
                expressiveness,
                presence,
                tone,
                suggestion
            ) = analyze_accent(transcript)

            st.success("✅ Analiz Tamamlandı!")

            st.markdown("### 📄 Video İçerik Özeti")
            st.write(summary)

            st.markdown("### 🎙️ Konuşma Analizi")
            st.markdown(f"- **Clarity of Speech:** {clarity}/10")
            st.markdown(f"- **Diction & Pronunciation:** {diction}/10")
            st.markdown(f"- **Expressiveness:** {expressiveness}/10")
            st.markdown(f"- **Confidence / Presence:** {presence}/10")
            st.markdown(f"- **🎭 Emotional Tone:** _{tone}_")
            st.markdown(f"- **💡 Suggestion for Improvement:** _{suggestion}_")

        except Exception as e:
            st.error(f"❌ Hata oluştu:\n\n{str(e)}")
