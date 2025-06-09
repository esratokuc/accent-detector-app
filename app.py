import streamlit as st
import uuid
from utils import (
    download_video,
    extract_audio_from_video,
    transcribe_audio_whisper,
    analyze_accent_local,
    export_results_to_pdf,
    send_email_with_pdf
)

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (Offline Whisper Model)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            audio_path = extract_audio_from_video(video_path)
            transcript = transcribe_audio_whisper(audio_path)
            results = analyze_accent_local(transcript)

            st.success("✅ Analysis Complete!")
            for res in results:
                st.markdown(f"**🗣️ Accent:** `{res['accent']}`")
                st.markdown(f"**📊 Confidence:** `{res['confidence']}%`")
                st.markdown(f"**🧠 Explanation:** _{res['explanation']}_")
                st.markdown(f"**📄 Segment:** _{res['segment']}_")
                st.markdown("---")

            # PDF Export and Email
            with st.form("email_form"):
                st.markdown("📩 Send Results by Email")
                recipient = st.text_input("Recipient Email")
                sender = st.text_input("Your Gmail", placeholder="example@gmail.com")
                password = st.text_input("App Password", type="password")
                submitted = st.form_submit_button("Send PDF")

                if submitted:
                    with st.spinner("✉️ Sending email..."):
                        pdf_path = export_results_to_pdf(results)
                        send_email_with_pdf(recipient, pdf_path, sender, password)
                        st.success("📤 Email sent!")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")
