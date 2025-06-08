import streamlit as st
from utils import download_video, transcribe_audio, analyze_accent
import uuid

st.set_page_config(page_title="Accent & Speech Analyzer", layout="centered")
st.title("🗣️ English Accent & Speech Insight Tool")

video_url = st.text_input("🎬 Enter a public video URL (MP4 format recommended):")

if st.button("Analyze") and video_url:
    with st.spinner("Processing video..."):
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

            st.success("✅ Analysis Complete!")
            st.markdown(f"**🎯 Accent:** `{accent}`")
            st.markdown(f"**📊 Confidence:** `{confidence}%`")
            st.markdown(f"**🧠 Explanation:** _{explanation}_")

            st.markdown("---")
            st.markdown("### 📄 What is this video about?")
            st.info(summary)

            st.markdown("---")
            st.markdown("### 🗣️ Speaker Evaluation")
            st.markdown(f"- **Clarity of Speech:** {clarity}/10")
            st.markdown(f"- **Diction & Pronunciation:** {diction}/10")
            st.markdown(f"- **Expressiveness:** {expressiveness}/10")
            st.markdown(f"- **Confidence / Presence:** {presence}/10")
            st.markdown(f"- **🎭 Emotional Tone:** _{tone}_")
            st.markdown(f"- **💡 Suggestion:** _{suggestion}_")

        except Exception as e:
            st.error(f"An error occurred:\n\n{str(e)}")
