import streamlit as st
from utils import (
    download_video,
    transcribe_audio,
    analyze_accent,
    export_results_to_pdf,
    send_email_with_pdf
)
import uuid
import os
from dotenv import load_dotenv

# Load secrets if local
load_dotenv()

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (via URL)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

# Store results in session
if "result" not in st.session_state:
    st.session_state.result = None

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            transcript = transcribe_audio(video_path)
            results = analyze_accent(transcript)

            st.session_state.result = {
                "results": results,
                "transcript": transcript
            }

            st.success("✅ Analysis Complete!")

            for idx, res in enumerate(results):
                st.markdown(f"### 🧩 Segment {idx + 1}")
                st.markdown(f"**🗣️ Detected Accent:** `{res['accent']}`")
                st.markdown(f"**📊 Confidence Score:** `{res['confidence']}%`")
                st.markdown(f"**🧠 Explanation:** _{res['explanation']}_")
                st.markdown("---")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")

# Show PDF + email area after analysis
if st.session_state.result:
    st.subheader("📧 Get Report by Email")
    recipient_email = st.text_input("Enter your email to receive the PDF report:")

    if st.button("📤 Send PDF Report") and recipient_email:
        try:
            pdf_path = export_results_to_pdf(
                st.session_state.result["results"],
                st.session_state.result["transcript"]
            )

            sender_email = os.getenv("SENDER_EMAIL")
            sender_password = os.getenv("SENDER_PASSWORD")

            send_email_with_pdf(
                recipient_email,
                pdf_path,
                sender_email,
                sender_password
            )
            st.success(f"📩 Report sent to {recipient_email}")
        except Exception as e:
            st.error(f"❌ Failed to send email:\n\n{str(e)}")
