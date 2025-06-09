import streamlit as st
import uuid
from utils import (
    download_video,
    extract_audio,
    transcribe_audio_whisper,
    analyze_accent_local,
    export_results_to_pdf,
    send_email_with_pdf,
)

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (Offline Whisper)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)
            audio_path = extract_audio(video_path)

            transcript = transcribe_audio_whisper(audio_path)
            results = analyze_accent_local(transcript)

            st.success("✅ Analysis Complete!")
            for idx, res in enumerate(results):
                st.markdown(f"**🎯 Segment {idx+1}:**")
                st.markdown(f"- **Accent:** `{res['accent']}`")
                st.markdown(f"- **Confidence:** `{res['confidence']}%`")
                st.markdown(f"- **Explanation:** _{res['explanation']}_")
                st.markdown("---")

            # PDF Export
            pdf_file = export_results_to_pdf(results)
            with open(pdf_file, "rb") as f:
                st.download_button("📄 Download PDF Report", f, file_name=pdf_file)

            # Optional email
            st.markdown("📧 If you want to receive the PDF via email:")
            recipient_email = st.text_input("Your Email Address")
            sender_email = st.text_input("Sender Gmail", type="password")
            sender_pass = st.text_input("Sender Gmail Password", type="password")
            if st.button("Send Report to My Email") and recipient_email:
                send_email_with_pdf(recipient_email, pdf_file, sender_email, sender_pass)
                st.success("📬 Email sent successfully!")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")
