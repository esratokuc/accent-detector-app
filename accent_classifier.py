
import os
from openai import OpenAI
from faster_whisper import WhisperModel

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
model = WhisperModel("base", device="cpu", compute_type="int8")

def classify_accent(audio_path):
    segments, info = model.transcribe(audio_path, beam_size=5)
    transcription = " ".join([segment.text for segment in segments])

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an English accent classification assistant. Analyze the text and determine whether the speaker has a British, American, or other English accent. Give a confidence score from 0 to 100 and provide a 1-sentence summary."
            },
            {"role": "user", "content": transcription}
        ]
    )

    message = completion.choices[0].message.content

    # Simple parsing (improve if needed)
    accent = "Unknown"
    confidence = 0
    summary = message

    if "American" in message:
        accent = "American"
    elif "British" in message:
        accent = "British"
    elif "Australian" in message:
        accent = "Australian"
    elif "Non-English" in message:
        accent = "Non-English"

    import re
    match = re.search(r"(\d{1,3})%", message)
    if match:
        confidence = int(match.group(1))

    return {
        "accent": accent,
        "confidence": confidence,
        "summary": summary
    }
