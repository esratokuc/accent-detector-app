import streamlit as st
from utils import process_video_and_analyze
from utils_pdf import export_results_to_pdf, send_email_with_attachment
import os

st.set_page_config(page_title="Accent & Emotion Analyzer", layout="centered")
st.title("🎙️ English Accent Analyzer")

video_url = st.text_input("📎 Enter a public video URL (MP4):")

recipient_email = st.text_input("📧 Enter your email to receive the PDF report (optional):")

if st.button("Analyze") and video_url:
    with st.spinner("🔄 Processing video and analyzing..."):
        results = process_video_and_analyze(video_url)

    st.success("✅ Analysis complete!")

    for spk, data in results.items():
        st.markdown(f"### 🧑 {spk}")
        st.markdown(f"- **Accent:** `{data['accent']}`")
        st.markdown(f"- **Sentiment:** `{data['sentiment']}`")
        st.markdown(f"- **Summary:** _{data['explanation']}_")
        st.markdown("#### Transcript:")
        for seg in data["segments"]:
            st.markdown(f"🗨️ {seg['text']}")

    with st.spinner("📄 Generating PDF..."):
        pdf_path = export_results_to_pdf(results)

    with open(pdf_path, "rb") as file:
        st.download_button(
            label="📥 Download PDF Report",
            data=file,
            file_name="accent_report.pdf",
            mime="application/pdf"
        )

    if recipient_email:
        with st.spinner("📧 Sending email..."):
            sender_email = os.getenv("SENDER_EMAIL")
            sender_password = os.getenv("SENDER_PASSWORD")
            send_email_with_attachment(recipient_email, pdf_path, sender_email, sender_password)
            st.success(f"📩 PDF sent to {recipient_email}")
