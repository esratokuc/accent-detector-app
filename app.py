import streamlit as st
import os
from audio_utils import extract_audio
from accent_classifier import classify_accent
import urllib.request

st.title("Accent Detector")

video_url = st.text_input("Enter public video URL (MP4 or Loom):")

if video_url:
    st.info("Downloading video...")
    video_path = "downloaded_video.mp4"
    urllib.request.urlretrieve(video_url, video_path)

    st.success("Video downloaded. Extracting audio...")
    audio_path = extract_audio(video_path)

    st.success("Audio extracted. Classifying accent...")
    result = classify_accent(audio_path)

    st.subheader("Result:")
    st.write(f"**Accent:** {result['accent']}")
    st.write(f"**Confidence:** {result['confidence']}%")
    st.write(f"**Summary:** {result['summary']}")
