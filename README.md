# YouTube Summarizer AI 🎬

An AI-powered YouTube video summarizer built with Streamlit and Groq (LLaMA 3).

## Features
- Paste any YouTube URL and get an instant summary
- Key points extraction
- Ask questions about the video content
- Clean, modern dark UI

## Tech Stack
- **Frontend:** Streamlit
- **AI Model:** LLaMA 3 via Groq API
- **Transcript:** yt-dlp
- **Language:** Python

## Setup
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API key:
```
   GROQ_API_KEY=your_key_here
```
4. Run: `streamlit run app.py`