import streamlit as st
from audio_utils import extract_audio
from accent_classifier import classify_accent
import tempfile

st.title("🎙️ English Accent Classifier")

video_url = st.text_input("Paste a public video URL (MP4, etc.)")

if st.button("Analyze") and video_url:
    with st.spinner("Downloading and extracting audio..."):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_video:
            # Download video
            import requests
            r = requests.get(video_url)
            tmp_video.write(r.content)
            tmp_video.flush()

            # Extract audio
            audio_path = extract_audio(tmp_video.name)

    with st.spinner("Transcribing and classifying..."):
        result = classify_accent(audio_path)

    st.success("🎯 Result")
    st.markdown(f"**Accent:** {result['accent']}")
    st.markdown(f"**Confidence:** {result['confidence']}%")
    st.markdown(f"**Summary:** {result['summary']}")
