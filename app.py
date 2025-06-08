import streamlit as st
from utils import download_video, transcribe_audio, analyze_accent
import uuid

st.set_page_config(page_title="Video and Accent Analyze", layout="centered")
st.title("Video and Accent Analyze")

video_url = st.text_input("Enter a public MP4 video URL:")

if st.button("Analyze"):
    with st.spinner("Analyzing the video content and speaker style..."):
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
                suggestion
            ) = analyze_accent(transcript)

            st.success("Analysis complete.")

            st.markdown("### Content Summary")
            st.write(summary)

            st.markdown("### Speaking Style Evaluation")
            st.markdown(f"- **Clarity of Speech:** {clarity}/10")
            st.markdown(f"- **Diction & Pronunciation:** {diction}/10")
            st.markdown(f"- **Expressiveness:** {expressiveness}/10")
            st.markdown(f"- **Confidence / Presence:** {presence}/10")
            st.markdown(f"- **Emotional Tone:** _{tone}_")
            st.markdown(f"- **Improvement Suggestion:** _{suggestion}_")

        except Exception as e:
            st.error(f"An error occurred:\n\n{str(e)}")
