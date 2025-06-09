import streamlit as st
from utils import download_video, send_to_assemblyai, analyze_accent_from_transcript
import uuid
import os

st.set_page_config(page_title="Accent Detector", layout="centered")
st.title("🎙️ Multi-Speaker English Accent Detector")

st.markdown("""
Paste a public video URL (MP4 format) where multiple people are speaking English.  
The app will detect each speaker's **accent** individually and show confidence scores.
""")

video_url = st.text_input("📎 Enter a public video URL (e.g., Loom, Dropbox, direct link):")

if "result" not in st.session_state:
    st.session_state.result = None

if st.button("🔍 Analyze Accent") and video_url:
    with st.spinner("Downloading & analyzing video..."):
        try:
            video_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
            video_path = download_video(video_url, filename=video_filename)

            json_result = send_to_assemblyai(video_path)

            speakers = {}
            for utterance in json_result["utterances"]:
                text = utterance.get("text", "").strip()
                if text.startswith("[") or not text:  # Skip [laughter], [music], etc.
                    continue
                speaker = utterance['speaker']
                speakers.setdefault(speaker, "")
                speakers[speaker] += " " + text

            results = []
            for spk, text in speakers.items():
                accent, score = analyze_accent_from_transcript(text)
                results.append({
                    "speaker": spk,
                    "transcript": text,
                    "accent": accent,
                    "score": score
                })

            st.session_state.result = results
            st.success("✅ Analysis Complete!")

        except Exception as e:
            st.error(f"❌ Error during processing:\n\n{str(e)}")

# 🔎 Result display
if st.session_state.result:
    st.subheader("🧑‍⚕️ Detected Speaker Accents")
    for item in st.session_state.result:
        st.markdown(f"---")
        st.markdown(f"### 🗣️ Speaker {item['speaker']}")
        st.markdown(f"- **Accent:** `{item['accent']}`")
        st.markdown(f"- **Confidence Score:** `{item['score']}%`")
        with st.expander("📝 Full Transcript"):
            st.write(item['transcript'])

    # Optional PDF/Email feature can be added here
