import streamlit as st
from utils import (
    download_video,
    transcribe_audio,
    analyze_segments,
    export_results_to_pdf,
    send_email_with_pdf
)
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent & Emotion Detector (via URL)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if "results" not in st.session_state:
    st.session_state.results = None

if st.button("Analyze Video") and video_url:
    with st.spinner("🔄 Processing video..."):
        try:
            filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            path = download_video(video_url, filename=filename)
            transcript = transcribe_audio(path)
            results = analyze_segments(transcript)
            st.session_state.results = results
            st.success("✅ Analysis complete!")

            for idx, item in enumerate(results):
                st.markdown(f"**🧩 Segment {idx + 1}:**")
                st.markdown(f"`{item['segment']}`")
                st.markdown(f"💬 {item['analysis']}")
                st.markdown("---")

        except Exception as e:
            st.error(f"❌ Error: {e}")

if st.session_state.results:
    st.subheader("📧 Get Your PDF Report")
    email = st.text_input("Enter your email:")
    if st.button("📤 Send PDF") and email:
        try:
            pdf_path = export_results_to_pdf(st.session_state.results)
            send_email_with_pdf(
                recipient_email=email,
                pdf_path=pdf_path,
                sender_email=os.getenv("SENDER_EMAIL"),
                sender_password=os.getenv("SENDER_PASSWORD")
            )
            st.success(f"📩 Report sent to {email}")
        except Exception as e:
            st.error(f"❌ Failed to send email:\n\n{str(e)}")
