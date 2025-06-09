import streamlit as st
from utils import process_video_and_analyze

st.set_page_config(page_title="Accent & Emotion Detector", layout="centered")
st.title("🎙️ English Accent & Emotion Analyzer")
st.markdown("Paste a **public video URL** (MP4 or YouTube) for analysis:")

video_url = st.text_input("Video URL")

if st.button("Analyze") and video_url:
    with st.spinner("🔄 Processing video and analyzing..."):
        segments = process_video_and_analyze(video_url)

    st.success("✅ Analysis complete!")

    for speaker_id, data in segments.items():
        st.markdown(f"## 🧑 Speaker {speaker_id + 1}")
        st.markdown(f"- **Accent**: {data['accent']}")
        st.markdown(f"- **Emotion**: {data['emotion']}")
        st.markdown(f"- **Summary**: {data['summary']}")
        st.markdown("#### Transcript:")
        for seg in data["segments"]:
            st.markdown(f"🗨️ {seg}")
