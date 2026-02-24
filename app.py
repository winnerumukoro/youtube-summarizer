# app.py
# Main Streamlit UI for YouTube Summarizer

import streamlit as st
from summarizer import (
    extract_video_id,
    get_transcript,
    summarize_transcript,
    answer_question,
    get_video_stats
)

# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="YouTube Summarizer AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #ff0000 0%, #ff6b6b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #888;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .summary-box {
        background-color: #1e1e2e;
        border-left: 4px solid #ff0000;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #ffffff;
    }
    .answer-box {
        background-color: #1e1e2e;
        border-left: 4px solid #4CAF50;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #ffffff;
    }
    .stat-box {
        background-color: #1e1e2e;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "video_id" not in st.session_state:
    st.session_state.video_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<h1 class="main-header">🎬 YouTube Summarizer AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Paste any YouTube URL and get an instant AI-powered summary</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# URL INPUT
# ─────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )
with col2:
    summarize_btn = st.button("Summarize", type="primary", use_container_width=True)

# ─────────────────────────────────────────────
# MAIN LOGIC
# ─────────────────────────────────────────────
if summarize_btn and url:
    # Extract video ID
    video_id = extract_video_id(url)

    if not video_id:
        st.error("Invalid YouTube URL. Please check and try again.")
    else:
        with st.spinner("Fetching transcript and generating summary..."):
            # Step 1: Get transcript
            transcript, error = get_transcript(video_id)

            if error:
                st.error(f"Could not fetch transcript: {error}")
            else:
                # Step 2: Summarize
                summary = summarize_transcript(transcript)

                # Save to session state
                st.session_state.transcript = transcript
                st.session_state.summary = summary
                st.session_state.video_id = video_id
                st.session_state.chat_history = []

# ─────────────────────────────────────────────
# DISPLAY RESULTS
# ─────────────────────────────────────────────
if st.session_state.summary:
    st.markdown("---")

    # Show embedded video + stats side by side
    col1, col2 = st.columns([2, 1])

    with col1:
        st.video(f"https://www.youtube.com/watch?v={st.session_state.video_id}")

    with col2:
        stats = get_video_stats(st.session_state.transcript)
        st.markdown("### Video Stats")
        st.markdown(f"""
        <div class="stat-box">
            <h2>{stats['word_count']:,}</h2>
            <p>Words in transcript</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        st.markdown(f"""
        <div class="stat-box">
            <h2>~{stats['reading_time']} min</h2>
            <p>Reading time saved</p>
        </div>
        """, unsafe_allow_html=True)

    # Show summary
    st.markdown("### AI Summary")
    st.markdown(f'<div class="summary-box">{st.session_state.summary}</div>',
                unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # Q&A SECTION
    # ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Ask a Question About This Video")
    st.write("Want to know something specific? Ask anything about the video content!")

    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        with st.chat_message("assistant", avatar="🎬"):
            st.markdown(f'<div class="answer-box">{chat["answer"]}</div>',
                       unsafe_allow_html=True)

    # Question input
    question = st.chat_input("Ask something about the video...")
    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant", avatar="🎬"):
            with st.spinner("Thinking..."):
                answer = answer_question(st.session_state.transcript, question)
            st.markdown(f'<div class="answer-box">{answer}</div>',
                       unsafe_allow_html=True)

        st.session_state.chat_history.append({
            "question": question,
            "answer": answer
        })

elif not summarize_btn:
    # Show instructions when no video is loaded
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### 📋 Step 1
        **Paste a YouTube URL**
        Copy any YouTube video link and paste it above
        """)
    with col2:
        st.markdown("""
        ### ⚡ Step 2
        **Click Summarize**
        Our AI fetches the transcript and generates a summary instantly
        """)
    with col3:
        st.markdown("""
        ### 💬 Step 3
        **Ask Questions**
        Dive deeper by asking anything about the video content
        """)