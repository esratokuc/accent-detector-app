import streamlit as st
from utils import download_video, transcribe_audio, analyze_accent
import uuid

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (via URL)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            transcript = transcribe_audio(video_path)
            accent, confidence, explanation = analyze_accent(transcript)

            st.success("✅ Analysis Complete!")
            st.markdown(f"**🗣️ Detected Accent:** `{accent}`")
            st.markdown(f"**📊 Confidence Score:** `{confidence}%`")
            st.markdown(f"**🧠 Explanation:** _{explanation}_")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")
