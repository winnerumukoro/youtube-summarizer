# summarizer.py
import yt_dlp
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, MAX_TRANSCRIPT_LENGTH
import re
import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def extract_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            'writeautomaticsub': True,
            'writesubtitles': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            subtitles = info.get('subtitles') or {}
            auto_captions = info.get('automatic_captions') or {}

            # Prefer manual subtitles, fall back to auto-generated
            en_subs = subtitles.get('en') or auto_captions.get('en')

            if not en_subs:
                return None, "No English transcript found for this video."

            # Get json3 format
            for fmt in en_subs:
                if fmt.get('ext') == 'json3':
                    with urllib.request.urlopen(fmt['url']) as response:
                        data = json.loads(response.read())

                    text = ' '.join([
                        event.get('segs', [{}])[0].get('utf8', '')
                        for event in data.get('events', [])
                        if event.get('segs')
                    ])
                    return text.strip(), None

            return None, "Could not extract transcript text."

    except Exception as e:
        return None, f"Error fetching transcript: {str(e)}"


def summarize_transcript(transcript):
    if len(transcript) > MAX_TRANSCRIPT_LENGTH:
        transcript = transcript[:MAX_TRANSCRIPT_LENGTH] + "..."

    prompt = f"""You are an expert at summarizing YouTube videos clearly and concisely.

Given the following video transcript, provide:

1. **Video Summary** (3-4 sentences capturing the main idea)
2. **Key Points** (5-7 bullet points of the most important takeaways)
3. **Who Should Watch This** (1-2 sentences about the target audience)
4. **Key Quotes** (2-3 interesting or important quotes from the transcript)

TRANSCRIPT:
{transcript}

Provide a well-structured, clear response."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500
    )
    return response.choices[0].message.content


def answer_question(transcript, question):
    if len(transcript) > MAX_TRANSCRIPT_LENGTH:
        transcript = transcript[:MAX_TRANSCRIPT_LENGTH] + "..."

    prompt = f"""You are a helpful assistant answering questions about a YouTube video.
Use ONLY the transcript below to answer the question.
If the answer isn't in the transcript, say so clearly.

TRANSCRIPT:
{transcript}

QUESTION: {question}

ANSWER:"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=800
    )
    return response.choices[0].message.content


def get_video_stats(transcript):
    word_count = len(transcript.split())
    reading_time = round(word_count / 200)
    return {
        "word_count": word_count,
        "reading_time": reading_time
    }