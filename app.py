import streamlit as st
from utils import (
    download_video,
    transcribe_audio,
    analyze_accent
)
import uuid

st.set_page_config(page_title="English Accent Analyzer", layout="centered")
st.title("🗣️ English Accent Analyzer")

st.markdown("Enter a public **video URL** (e.g., MP4 or Loom) to analyze the **speaker's English accent** and get a summary.")

video_url = st.text_input("🎥 Video URL")

if st.button("Analyze") and video_url:
    with st.spinner("⏳ Downloading and processing video..."):
        try:
            # Download and process
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            transcript = transcribe_audio(video_path)
            accent, confidence, explanation, summary, clarity, diction, expressiveness, video_description = analyze_accent(transcript)

            # Display results
            st.success("✅ Analysis complete!")

            st.markdown("### 🗣️ Accent Analysis")
            st.markdown(f"**Accent:** `{accent}`")
            st.markdown(f"**Confidence Score:** `{confidence}%`")
            st.markdown(f"**Explanation:** _{explanation}_")

            st.markdown("### 🧾 Transcript Summary")
            st.markdown(summary if summary else "_Not available_")

            st.markdown("### 📊 Speaking Evaluation")
            st.markdown(f"**Clarity:** `{clarity}`")
            st.markdown(f"**Diction & Pronunciation:** `{diction}`")
            st.markdown(f"**Expressiveness:** `{expressiveness}`")

            st.markdown("### 🎬 Video Description")
            st.markdown(video_description if video_description else "_Not available_")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")
