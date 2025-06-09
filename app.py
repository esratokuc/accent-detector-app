import streamlit as st
from utils import download_video, transcribe_audio_whisper, analyze_accent_local, export_results_to_pdf, send_email_with_pdf
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (Offline Model)")

video_url = st.text_input("📎 Enter a public video URL (MP4, etc.):")

if "results" not in st.session_state:
    st.session_state.results = None

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            path = download_video(video_url, filename)

            transcript = transcribe_audio_whisper(path)
            results = analyze_accent_local(transcript)

            st.session_state.results = results
            st.success("✅ Accent analysis complete!")

            for idx, res in enumerate(results):
                st.markdown(f"**Segment {idx+1}:**")
                st.markdown(f"🗣️ Accent: `{res['accent']}`")
                st.markdown(f"📊 Confidence: `{res['confidence']}%`")
                st.markdown(f"🧠 {res['explanation']}`")
                st.markdown("---")

            st.info("🔎 Accent predictions are based on **text analysis** only. In multi-speaker videos, different accents may be detected per segment.")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# PDF ve e-posta gönderme
if st.session_state.results:
    st.subheader("📧 Send Report via Email")
    recipient = st.text_input("Your email address:")
    if st.button("📤 Send Report") and recipient:
        try:
            pdf = export_results_to_pdf(st.session_state.results)
            sender = os.getenv("SENDER_EMAIL")
            password = os.getenv("SENDER_PASSWORD")
            send_email_with_pdf(recipient, pdf, sender, password)
            st.success(f"📩 Report sent to {recipient}")
        except Exception as e:
            st.error(f"❌ Email send failed:\n{e}")
