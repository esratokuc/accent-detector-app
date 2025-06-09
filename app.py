import streamlit as st
from utils import download_video, transcribe_audio, split_transcript_by_segments, analyze_accent
from utils_pdf import export_results_to_pdf, send_email_with_pdf
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (via URL)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if "result" not in st.session_state:
    st.session_state.result = None

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            transcript = transcribe_audio(video_path)
            segments = split_transcript_by_segments(transcript)
            analyses = []

            for idx, segment in enumerate(segments):
                accent, confidence, explanation = analyze_accent(segment)
                analyses.append({
                    "segment": segment,
                    "accent": accent,
                    "confidence": confidence,
                    "explanation": explanation
                })

            st.session_state.result = {
                "analyses": analyses,
                "full_transcript": transcript
            }

            st.success("✅ Analysis Complete!")
            for i, res in enumerate(analyses):
                st.markdown(f"### 🎧 Speaker {i+1}")
                st.markdown(f"**Accent:** `{res['accent']}`")
                st.markdown(f"**Confidence:** `{res['confidence']}%`")
                st.markdown(f"**Explanation:** _{res['explanation']}_")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")

if st.session_state.result:
    st.subheader("📧 Get Report by Email")
    recipient_email = st.text_input("Enter your email to receive the PDF report:")

    if st.button("📤 Send PDF Report") and recipient_email:
        try:
            sender_email = os.getenv("SENDER_EMAIL")
            sender_password = os.getenv("SENDER_PASSWORD")

            pdf_path = export_results_to_pdf(
                st.session_state.result["analyses"],
                st.session_state.result["full_transcript"]
            )

            send_email_with_pdf(recipient_email, pdf_path, sender_email, sender_password)
            st.success(f"📩 Report sent to {recipient_email}")
        except Exception as e:
            st.error(f"❌ Failed to send email:\n\n{str(e)}")
