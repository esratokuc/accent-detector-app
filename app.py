import streamlit as st
from utils import (
    download_video,
    transcribe_audio,
    analyze_accent
)
import uuid

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent & Video Summary Analyzer")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if st.button("Analyze Video") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
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
                suggestion,
                video_description
            ) = analyze_accent(transcript)

            st.success("✅ Analysis Complete!")

            st.markdown("### 🗣️ Accent Analysis")
            st.markdown(f"**Accent:** `{accent}`")
            st.markdown(f"**Confidence Score:** `{confidence}%`" if confidence else "**Confidence Score:** Not available")
            st.markdown(f"**Explanation:** _{explanation}_")

            st.markdown("### 🧾 Transcript Summary")
            st.markdown(f"> {summary}")

            st.markdown("### 📊 Speaking Evaluation")
            st.markdown(f"- **Clarity:** {clarity}/10" if clarity else "- **Clarity:** Not available")
            st.markdown(f"- **Diction & Pronunciation:** {diction}/10" if diction else "- **Diction & Pronunciation:** Not available")
            st.markdown(f"- **Expressiveness:** {expressiveness}/10" if expressiveness else "- **Expressiveness:** Not available")
            st.markdown(f"- **Confidence / Presence:** {presence}/10" if presence else "- **Confidence / Presence:** Not available")
            st.markdown(f"- **Tone:** _{tone}_")

            st.markdown("### 💡 Suggested Improvement")
            st.markdown(f"_{suggestion}_")

            st.markdown("### 🎬 YouTube-style Video Description")
            st.info(video_description)

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")
