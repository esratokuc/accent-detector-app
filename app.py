import streamlit as st
from utils import download_video, transcribe_audio, analyze_accent
import uuid

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent & Speech Analyzer")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if st.button("Analyze Video") and video_url:
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
                presence,
                tone,
                video_description
            ) = analyze_accent(transcript)

            st.success("✅ Analysis Complete!")

            st.header("🗣️ Accent Analysis")
            st.markdown(f"**Accent:** {accent}")
            st.markdown(f"**Confidence Score:** {confidence}%" if confidence != "Not available" else "**Confidence Score:** Not available")
            st.markdown(f"**Explanation:** _{explanation}_")

            st.header("🧾 Transcript Summary")
            st.markdown(summary if summary else "Not available")

            st.header("📊 Speaking Evaluation")
            st.markdown(f"- **Clarity:** {clarity}")
            st.markdown(f"- **Diction & Pronunciation:** {diction}")
            st.markdown(f"- **Expressiveness:** {expressiveness}")
            st.markdown(f"- **Confidence / Presence:** {presence}")
            st.markdown(f"- **Tone:** {tone}")

            st.header("🎬 Video Description")
            st.markdown(video_description if video_description else "Not available")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")
