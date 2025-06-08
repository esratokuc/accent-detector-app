import streamlit as st
from utils import download_video, extract_audio, transcribe_audio, analyze_accent

st.title("English Accent Detector")

video_url = st.text_input("Enter public video URL (MP4 or Loom):")

if st.button("Analyze"):
    with st.spinner("Processing..."):
        video_path = download_video(video_url)
        audio_path = extract_audio(video_path)
        transcript = transcribe_audio(audio_path)
        accent, confidence, explanation = analyze_accent(transcript)

        st.success("Analysis Complete!")
        st.markdown(f"**Accent:** {accent}")
        st.markdown(f"**Confidence:** {confidence}%")
        st.markdown(f"**Explanation:** {explanation}")
