import streamlit as st
from utils import download_video, transcribe_audio_whisper, summarize_text

st.set_page_config(page_title="Accent + Summary Analyzer")
st.title("🎙️ English Accent & Summary Detector")

video_url = st.text_input("🔗 Paste a public video URL (MP4):")

if st.button("Analyze") and video_url:
    with st.spinner("Downloading and analyzing..."):
        try:
            audio_path = download_video(video_url)
            transcript = transcribe_audio_whisper(audio_path)
            summary = summarize_text(transcript)

            st.success("✅ Analysis Complete")
            st.subheader("Transcript")
            st.text_area("Transcript", value=transcript, height=300)

            st.subheader("Summary")
            st.text_area("Summary", value=summary, height=150)

        except Exception as e:
            st.error(f"❌ Error: {e}")
