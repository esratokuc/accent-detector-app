import streamlit as st
import os
from utils import download_video, process_video_and_analyze
from utils_pdf import generate_pdf_report, send_report_email

st.set_page_config(page_title="English Accent Analyzer", layout="centered")
st.title("🎙️ English Accent Analyzer")

video_url = st.text_input("🔗 Enter a public video URL (MP4):")

if st.button("Analyze") and video_url:
    with st.spinner("🔍 Processing video..."):
        try:
            results, full_text = process_video_and_analyze(video_url)
            st.session_state.results = results
            st.session_state.full_text = full_text
            st.session_state.pdf_path = generate_pdf_report(results, full_text)

            st.success("✅ Analysis Complete!")

            for speaker in results:
                st.markdown(f"""
                ### 🧩 {speaker['speaker']}
                - 🗣️ **Accent:** {speaker['accent']}
                - 📊 **Confidence:** {speaker['confidence']}%
                - 😊 **Sentiment:** {speaker['sentiment']}
                - 🧠 **Summary:** {speaker['explanation']}
                """)

            st.markdown("#### 🗒️ Transcript Download")
            with open(st.session_state.pdf_path, "rb") as file:
                st.download_button(
                    label="📥 Download PDF Report (Full Video Text)",
                    data=file,
                    file_name="accent_analysis_report.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"❌ An error occurred during analysis: {e}")

# Only show email section after successful analysis
if "results" in st.session_state and st.session_state.get("pdf_path"):
    with st.expander("📧 Send Report via Email"):
        email = st.text_input("✉️ Enter your email to receive the PDF report:")
        if st.button("📤 Send PDF to Email") and email:
            try:
                send_report_email(email, st.session_state.pdf_path)
                st.success(f"📨 Report successfully sent to {email}")
            except Exception as e:
                st.error(f"❌ Failed to send email: {e}")
