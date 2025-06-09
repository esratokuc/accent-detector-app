import streamlit as st
from utils import (
    download_video,
    transcribe_audio,
    analyze_accent,
    export_results_to_pdf,
    send_email_with_pdf
)
import uuid

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (via URL)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

recipient_email = st.text_input("📬 Enter recipient email (to send report):")
sender_email = st.text_input("📤 Sender Gmail address:")
sender_password = st.text_input("🔐 Sender App Password:", type="password")

if st.button("Analyze Accent and Email Report") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            transcript = transcribe_audio(video_path)
            (
                accent,
                confidence,
                explanation,
                summary,
                clarity,
                diction,
                expressiveness,
                video_description,
                tone
            ) = analyze_accent(transcript)

            st.success("✅ Analysis Complete!")
            st.markdown(f"**🗣️ Accent:** `{accent}`")
            st.markdown(f"**📊 Confidence Score:** `{confidence}%`")
            st.markdown(f"**🧠 Explanation:** _{explanation}_")
            st.markdown(f"**📄 Summary:** {summary}")
            st.markdown(f"**🎯 Clarity / Diction / Expressiveness:** {clarity}/10 / {diction}/10 / {expressiveness}/10")
            st.markdown(f"**🎬 Video Description:** _{video_description}_")
            st.markdown(f"**🎭 Tone:** `{tone}`")

            # Export to PDF
            pdf_path = export_results_to_pdf(
                accent,
                confidence,
                explanation,
                summary,
                clarity,
                diction,
                expressiveness,
                video_description,
                tone
            )
            st.success("📄 PDF report generated.")

            # Send via email
            if recipient_email and sender_email and sender_password:
                send_email_with_pdf(
                    recipient_email=recipient_email,
                    pdf_path=pdf_path,
                    sender_email=sender_email,
                    sender_password=sender_password
                )
                st.success(f"📧 Report emailed to {recipient_email}")
            else:
                st.warning("⚠️ Please fill in all email fields to send the report.")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")
