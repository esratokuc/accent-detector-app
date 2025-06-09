import streamlit as st
from utils import (
    download_video,
    transcribe_audio,
    split_transcript_by_segments,
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
st.title("🎙️ English Accent Detector (Multi-speaker Support)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

# Store analysis result in session
if "results" not in st.session_state:
    st.session_state.results = None
if "full_transcript" not in st.session_state:
    st.session_state.full_transcript = ""

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            transcript = transcribe_audio(video_path)
            st.session_state.full_transcript = transcript

            segments = split_transcript_by_segments(transcript)
            results = []

            for i, segment in enumerate(segments):
                accent, confidence, explanation = analyze_accent(segment)
                results.append({
                    "segment": i + 1,
                    "text": segment,
                    "accent": accent,
                    "confidence": confidence,
                    "explanation": explanation
                })

            st.session_state.results = results
            st.success("✅ Analysis Complete!")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")

# Show results
if st.session_state.results:
    st.subheader("🔍 Accent Detection Results")
    for res in st.session_state.results:
        st.markdown(f"""
**🧩 Segment {res['segment']}**
- **Accent:** `{res['accent']}`
- **Confidence:** `{res['confidence']}%`
- **Explanation:** _{res['explanation']}_
""")
        with st.expander("📝 Transcript"):
            st.write(res["text"])

    # Email PDF
    st.subheader("📧 Get Report by Email")
    recipient_email = st.text_input("Enter your email to receive the PDF report:")

    if st.button("📤 Send PDF Report") and recipient_email:
        try:
            pdf_path = export_results_to_pdf(
                st.session_state.results,
                st.session_state.full_transcript
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
