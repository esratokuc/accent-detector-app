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

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (Multi-speaker)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            # 1. Video indir
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            # 2. Transkript oluştur
            full_transcript = transcribe_audio(video_path)

            # 3. Segmentlere böl
            segments = split_transcript_by_segments(full_transcript)

            # 4. Her segment için analiz
            results = []
            for i, seg in enumerate(segments, 1):
                accent, confidence, explanation = analyze_accent(seg)
                results.append((i, seg, accent, confidence, explanation))

            st.success("✅ All segments analyzed!")

            # 5. Sonuçları göster
            for i, seg, accent, confidence, explanation in results:
                st.markdown(f"---\n### 🎙️ Segment {i}")
                st.markdown(f"**Transcript:** {seg}")
                st.markdown(f"**Accent:** `{accent}`")
                st.markdown(f"**Confidence:** `{confidence}%`")
                st.markdown(f"**Explanation:** _{explanation}_")

            st.markdown("---")
            st.markdown("📩 If you'd like to receive this report as a PDF via email, enter your address below:")

            recipient = st.text_input("Your email address")
            sender = st.secrets.get("EMAIL_SENDER") or os.getenv("EMAIL_SENDER")
            password = st.secrets.get("EMAIL_PASSWORD") or os.getenv("EMAIL_PASSWORD")

            if st.button("Send PDF Report") and recipient and sender and password:
                pdf_file = export_results_to_pdf(results)
                send_email_with_pdf(recipient, pdf_file, sender, password)
                st.success("✅ Report sent to your email!")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")
