import streamlit as st
from audio_utils import extract_audio
from accent_classifier import classify_accent
import os

st.set_page_config(page_title="Accent Detector", page_icon="🗣️")
st.title("🗣️ English Accent Detector")

uploaded_file = st.file_uploader("Upload a video file (.mp4)", type=["mp4"])
if uploaded_file is not None:
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_file.read())

    st.info("Extracting audio...")
    audio_path = extract_audio("input_video.mp4")

    st.success("Audio extracted successfully. Classifying accent...")

    with st.spinner("Analyzing..."):
        result = classify_accent(audio_path)

    st.subheader("🎯 Result")
    st.markdown(f"**Accent:** {result['accent']}")
    st.markdown(f"**Confidence:** {result['confidence']}%")
    st.markdown(f"**Summary:** {result['summary']}")
