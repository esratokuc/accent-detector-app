import streamlit as st
import os
from utils import process_video_and_analyze
from utils_pdf import generate_pdf_report, send_report_email

st.set_page_config(page_title="English Accent Analyzer", layout="centered")
st.title("🎙️ English Accent Analyzer")

video_url = st.text_input("🔗 Enter a public video URL (MP4):")
email_input_visible = False

# İlk analiz yapılana kadar PDF ve e-posta alanı görünmesin
if "results" not in st.session_state:
    st.session_state.results = None
    st.session_state.full_text = ""
    st.session_state.pdf_path = None

if st.button("Analyze") and video_url:
    with st.spinner("📥 Downloading and transcribing video..."):
        results, full_text = process_video_and_analyze(video_url)
        st.session_state.results = results
        st.session_state.full_text = full_text

    st.success("✅ Analysis Complete!")

    for speaker, data in results.items():
        st.markdown(f"""
        ### 🧩 {speaker}
        - 🗣️ **Detected Accent:** {data['accent']}
        - 📊 **Confidence Score:** {data['confidence']}%
        - 😊 **Emotion:** {data['sentiment']}
        - 🧠 **Summary:** _{data['explanation']}_
        """)

    with st.spinner("📄 Generating PDF..."):
        st.session_state.pdf_path = generate_pdf_report(results, full_text)

# PDF ve e-posta alanı sadece analiz sonrası görünür
if st.session_state.pdf_path:
    st.markdown("### 📄 Download Transcript Report")
    with open(st.session_state.pdf_path, "rb") as f:
        st.download_button(
            label="📥 Download Full Report (with Transcript)",
            data=f,
            file_name="accent_analysis_report.pdf",
            mime="application/pdf"
        )

    with st.expander("📧 Send Report via Email"):
        recipient_email = st.text_input("✉️ Enter your email to receive the PDF report:")
        if st.button("📤 Send PDF to Email") and recipient_email:
            try:
                sender_email = os.getenv("SENDER_EMAIL")
                sender_password = os.getenv("SENDER_PASSWORD")
                send_report_email(recipient_email, st.session_state.pdf_path, sender_email, sender_password)
                st.success(f"📩 Report sent to {recipient_email}")
            except Exception as e:
                st.error(f"❌ Failed to send email:\n\n{str(e)}")
