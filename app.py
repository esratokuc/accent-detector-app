import streamlit as st
import os
from utils import download_video, transcribe_audio_whisper, segment_speakers_and_analyze, export_results_to_pdf

st.set_page_config(page_title="English Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (via URL)")
st.markdown("📎 Enter a public video URL (MP4, Loom, etc.):")

video_url = st.text_input("Video URL")

temp_video_path = "temp_video.mp4"

if st.button("Analyze") and video_url:
    with st.spinner("📥 Downloading video..."):
        download_video(video_url, temp_video_path)

    with st.spinner("🧠 Transcribing and analyzing..."):
        transcription = transcribe_audio_whisper(temp_video_path)
        analysis_results = segment_speakers_and_analyze(transcription)

    st.success("✅ Analysis Complete!")

    for idx, result in enumerate(analysis_results):
        st.markdown(f"""
        ### 🧩 Segment {idx + 1}
        - 🗣️ **Detected Accent:** {result['accent']}
        - 📊 **Confidence Score:** {result['confidence']}%
        - 😊 **Sentiment:** {result['sentiment']}
        - 🧠 **Explanation:** {result['explanation']}
        - 📜 **Transcript:** {result['segment']}
        """)

    with st.spinner("📄 Generating PDF report..."):
        report_path = export_results_to_pdf(analysis_results)

    with open(report_path, "rb") as file:
        st.download_button(
            label="📥 Download PDF Report",
            data=file,
            file_name="accent_analysis_report.pdf",
            mime="application/pdf"
        )
