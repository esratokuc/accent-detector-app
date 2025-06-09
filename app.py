import streamlit as st
from utils import download_video, transcribe_audio_whisper, analyze_accent_local
import uuid
import os
from dotenv import load_dotenv
from fpdf import FPDF
from utils import export_results_to_pdf, send_email_with_pdf

# Load secrets if local
load_dotenv()

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (via URL)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

# Bellekte analiz sonucu tutulsun
if "result" not in st.session_state:
    st.session_state.result = None

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            transcript = transcribe_audio_whisper(video_path)
            results = analyze_accent_local(transcript)

            st.session_state.result = results

            st.success("✅ Analysis Complete!")
            for idx, res in enumerate(results):
                st.markdown(f"### 🧩 Segment {idx + 1}")
                st.markdown(f"**🗣️ Detected Accent:** `{res['accent']}`")
                st.markdown(f"**📊 Confidence Score:** `{res['confidence']}%`")
                st.markdown(f"**🧠 Explanation:** _{res['explanation']}_")

            st.info("🔎 Accent predictions are based on **text analysis** only. In multi-speaker videos, different accents may be detected per segment.")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")

# PDF + Mail alanı sadece analiz yapılmışsa görünür
if st.session_state.result:
    st.subheader("📧 Get Report by Email")
    recipient_email = st.text_input("Enter your email to receive the PDF report:")

    if st.button("📤 Send PDF Report") and recipient_email:
        try:
            # PDF dosyasını oluştur
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = f"accent_report_{timestamp}.pdf"

            content = ""
            for idx, res in enumerate(st.session_state.result):
                content += f"Segment {idx + 1}\n"
                content += f"Accent: {res['accent']}\n"
                content += f"Confidence Score: {res['confidence']}%\n"
                content += f"Explanation: {res['explanation']}\n\n"

            with open(pdf_path, "w") as f:
                f.write(content)

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
