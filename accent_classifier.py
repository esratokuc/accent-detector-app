from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in English speech analysis."},
            {"role": "user", "content": f"""
Given the following English transcript, determine the speaker's English accent.
Options: American, British, Australian, Indian, Other.

Then give a confidence score (0-100%) and a 1-2 sentence summary of what is being said.

Transcript:
\"{text}\"

Return your response in JSON format like:
{{"accent": "...", "confidence": ..., "summary": "..."}}.
"""}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content
