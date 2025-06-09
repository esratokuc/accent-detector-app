import streamlit as st
import os
from utils import (
    download_video,
    transcribe_audio_whisper,
    analyze_by_unique_speakers,
    export_results_to_pdf,
    send_email_with_pdf
)

st.set_page_config(page_title="English Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (Multi-speaker)")
st.markdown("📎 Enter a public video URL (MP4, Loom, etc.):")

video_url = st.text_input("Video URL")
temp_video_path = "temp_video.mp4"

if "results" not in st.session_state:
    st.session_state.results = None

if st.button("Analyze") and video_url:
    with st.spinner("📥 Downloading video..."):
        download_video(video_url, temp_video_path)

    with st.spinner("🧠 Transcribing and analyzing..."):
        transcript = transcribe_audio_whisper(temp_video_path)
        analysis = analyze_by_unique_speakers(transcript)
        st.session_state.results = analysis

    st.success("✅ Analysis Complete!")

if st.session_state.results:
    for result in st.session_state.results:
        st.markdown(f"""
        ### 👤 Speaker {result['speaker_id']}
        - 🗣️ **Accent:** {result['accent']}
        - 📊 **Confidence:** {result['confidence']}%
        - 😊 **Sentiment:** {result['sentiment']}
        - 📘 **Summary:** {result['summary']}
        - 📜 **Excerpt:** `{result['segment'][:300]}...`
        """)
        st.markdown("---")

    with st.spinner("📄 Generating PDF..."):
        pdf_path = export_results_to_pdf(st.session_state.results)

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📥 Download PDF Report",
            data=f,
            file_name="accent_report.pdf",
            mime="application/pdf"
        )

    st.subheader("📧 Email this report")
    recipient = st.text_input("Enter email address to send the report:")
    if st.button("📤 Send Email") and recipient:
        try:
            send_email_with_pdf(recipient, pdf_path)
            st.success(f"📬 Report sent to {recipient}")
        except Exception as e:
            st.error(f"❌ Failed to send email: {e}")
