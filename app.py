import streamlit as st
import os
import urllib.request
from audio_utils import extract_audio
from accent_classifier import classify_accent

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🗣️ English Accent Detector")

video_url = st.text_input("🎥 Enter MP4 video URL:")

if video_url:
    try:
        st.info("📥 Downloading video...")
        video_path = os.path.join("/tmp", "input_video.mp4")
        urllib.request.urlretrieve(video_url, video_path)

        st.success("✅ Video downloaded.")
        st.info("🔊 Extracting audio...")
        audio_path = extract_audio(video_path)

        if not os.path.exists(audio_path):
            st.error("❌ Audio file was not created.")
        else:
            st.success("✅ Audio extracted.")
            st.info("🧠 Running accent classification...")
            result = classify_accent(audio_path)

            st.subheader("🎯 Result")
            st.write(f"**Accent:** {result['accent']}")
            st.write(f"**Confidence:** {result['confidence']}%")
            st.write(f"**Summary:** {result['summary']}")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
