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

# Load secrets locally if available
load_dotenv()

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (via URL)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if "results" not in st.session_state:
    st.session_state.results = None

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            transcript = transcribe_audio(video_path)
            results = analyze_accent(transcript)

            st.session_state.results = {
                "segments": results,
                "transcript": transcript
            }

            st.success("✅ Analysis Complete!")
            for idx, segment in enumerate(results, 1):
                st.markdown(f"""
**🧩 Segment {idx}**
- **🗣️ Detected Accent:** `{segment.get('accent', 'Not available')}`
- **📊 Confidence Score:** `{segment.get('confidence', 'Not available')}%`
- **🧠 Explanation:** _{segment.get('explanation', 'Not available')}_  
""")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")

# PDF + Mail alanı sadece analiz yapılmışsa görünür
if st.session_state.results:
    st.subheader("📧 Get Report by Email")
    recipient_email = st.text_input("Enter your email to receive the PDF report:")

    if st.button("📤 Send PDF Report") and recipient_email:
        try:
            # PDF dosyasını oluştur
            pdf_path = export_results_to_pdf(
                st.session_state.results["segments"],
                st.session_state.results["transcript"]
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
