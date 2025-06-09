import streamlit as st
from utils import (
    download_video,
    transcribe_audio,
    analyze_accent
)
import uuid

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ English Accent Detector (via URL)")

video_url = st.text_input("📎 Enter a public video URL (MP4, Loom, etc.):")

if st.button("Analyze Accent") and video_url:
    with st.spinner("🔄 Downloading and analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            result = analyze_accent(transcribe_audio(video_path))

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
            ) = result

            st.success("✅ Analysis Complete!")
            st.markdown(f"**🗣️ Detected Accent:** `{accent}`")
            st.markdown(f"**📊 Confidence Score:** `{confidence}%`")
            st.markdown(f"**ℹ️ Explanation:** _{explanation}_")
            st.markdown("---")
            st.markdown(f"**🧠 Summary:** _{summary}_")
            st.markdown(f"**🎭 Tone:** `{tone}`")
            st.markdown("---")
            st.markdown("### 🧪 Speech Quality Scores (0–10)")
            st.markdown(f"- Clarity: `{clarity}`")
            st.markdown(f"- Diction: `{diction}`")
            st.markdown(f"- Expressiveness: `{expressiveness}`")
            st.markdown("---")
            st.markdown(f"**🎞️ Suggested Video Description:** _{video_description}_")

        except Exception as e:
            st.error(f"❌ An error occurred:\n\n{str(e)}")
