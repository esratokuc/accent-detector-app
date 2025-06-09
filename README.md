# 🎙️ English Accent Analyzer

**English Accent Analyzer** is a Streamlit-based web application that analyzes the spoken accents, emotional tones, and summaries of speakers in any given video URL.

## 🚀 Features

- 🧠 **Speaker Diarization via AssemblyAI:** Automatically detects and separates speakers in the video.
- 🌍 **Accent Detection via OpenAI:** Identifies each speaker’s English accent (e.g., British, American, Indian).
- 😄 **Sentiment Analysis:** Classifies the tone (e.g., calm, excited, neutral) of each speaker.
- 📝 **Summary Generation:** Provides a short summary of what each speaker said.
- 📄 **PDF Report:** Download a detailed PDF report or send it via email.
- 📜 **Full Transcript Included:** The full transcript of the video is included in the PDF.

## 📷 Screenshot

<img width="892" alt="image" src="https://github.com/user-attachments/assets/fbbadef1-699b-452b-ad75-376b8a8f2499" />
<img width="892" alt="image" src="https://github.com/user-attachments/assets/cd102077-190b-4d86-acba-e026c0b1a425" />



## 🛠️ Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/accent-detector-app.git
   cd accent-detector-app
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.streamlit/secrets.toml` file with the following content:

```toml
OPENAI_API_KEY = "your-openai-api-key"
ASSEMBLYAI_API_KEY = "your-assemblyai-api-key"
SENDER_EMAIL = "youremail@gmail.com"
SENDER_PASSWORD = "your-app-password"
```

> 💡 For Gmail, you must use an **App Password**. [How to get one](https://support.google.com/accounts/answer/185833)

## ▶️ How to Run

```bash
streamlit run app.py
```

1. Enter a publicly accessible video URL (MP4, Loom, etc.).
2. Click “Analyze” to process the video and detect speaker accents, tone, and summaries.
3. Download the full PDF report or send it via email.

## 📁 Project Structure

```
accent-detector-app/
│
├── app.py              # Main Streamlit app interface
├── utils.py            # Video processing and accent analysis
├── utils_pdf.py        # PDF generation and email delivery
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🔐 Security Note

- No video data or API keys are stored.
- Only official APIs (OpenAI + AssemblyAI) are used for processing.

## 📄 License

MIT License. © 2025
