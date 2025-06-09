import streamlit as st
import uuid
from utils import (
    download_video,
    transcribe_audio_whisper,
    analyze_accent_local,
    export_results_to_pdf,
    send_email_with_pdf,
)

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (Local Whisper + Keyword Analysis)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            transcript = transcribe_audio_whisper(video_path)
            results = analyze_accent_local(transcript)

            st.success("✅ Analysis Complete!")
            for idx, res in enumerate(results):
                st.markdown(f"**Segment {idx + 1}:**")
                st.markdown(f"- **Accent:** `{res['accent']}`")
                st.markdown(f"- **Confidence:** `{res['confidence']}%`")
                st.markdown(f"- **Explanation:** _{res['explanation']}_")
                st.markdown("---")

            st.info("🔎 Accent predictions are based on **keyword-based text analysis** only. Not a deep AI model.")

            # E-posta gönderme seçeneği
            with st.form("email_form"):
                st.markdown("📧 **Would you like to receive the results as a PDF via email?**")
                recipient_email = st.text_input("Your Email")
                sender_email = st.text_input("Sender Gmail")
                sender_password = st.text_input("Sender App Password", type="password")
                submit_email = st.form_submit_button("Send Email")

                if submit_email:
                    with st.spinner("📤 Generating and sending PDF..."):
                        pdf_path = export_results_to_pdf(results)
                        send_email_with_pdf(recipient_email, pdf_path, sender_email, sender_password)
                        st.success(f"📩 PDF report sent to **{recipient_email}**!")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")
