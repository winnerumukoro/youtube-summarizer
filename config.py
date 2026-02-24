# config.py
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Try Streamlit secrets first (cloud), then .env (local)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq model - fast and free
GROQ_MODEL = "llama-3.3-70b-versatile"

# Max transcript length to send to AI
MAX_TRANSCRIPT_LENGTH = 12000