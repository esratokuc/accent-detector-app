
import streamlit as st
from accent_classifier import classify_accent
from audio_utils import extract_audio

st.title("🎙️ English Accent Analyzer")

video_file = st.file_uploader("Upload a video file (MP4)", type=["mp4"])
if video_file is not None:
    with open("temp_video.mp4", "wb") as f:
        f.write(video_file.read())
    st.success("Video uploaded!")

    audio_path = extract_audio("temp_video.mp4")
    st.info("Audio extracted. Analyzing...")

    result = classify_accent(audio_path)

    st.markdown("## 🎯 Result")
    st.markdown(f"**Accent:** {result['accent']}")
    st.markdown(f"**Confidence:** {result['confidence']}%")
    st.markdown(f"**Summary:** {result['summary']}")
