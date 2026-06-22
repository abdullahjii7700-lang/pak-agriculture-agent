
import streamlit as st
import google.generativeai as genai
import requests
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import os

# Pure Enterprise Call Screen Layout
st.set_page_config(page_title="Agri Call Agent", page_icon="📞", layout="centered")
st.title("📞 100% Free Agri Call Agent")
st.write("---")

# Secure Keys from Streamlit Secrets
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
WEATHER_KEY = st.secrets["WEATHER_KEY"]

# Configure AI Engine
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- AGENT KI PEHLI AWAZ KA JUGAAR ---
if "welcome_done" not in st.session_state:
    st.session_state.welcome_done = True
    
    # Pehla message jo Agent khud bolega
    welcome_text = "Assalam-o-Alaikum! Main aap ka Agriculture Agent hoon. Aaj main aap ki faslon ke baare mein kya madad kar sakta hoon?"
    
    # Audio generate karein aur play karein automatically
    tts = gTTS(text=welcome_text, lang='ur')
    tts.save("welcome.mp3")
    
    # Chupke se audio autoplay karne ka tarika
    st.audio("welcome.mp3", format="audio/mp3", autoplay=True)
    st.success(f"🤖 Agent: {welcome_text}")

st.write("---")
st.write("### 👇 Ab Aap Apni Baat Bolna Shuru Karein")

# Niche aap ka baaki mic_recorder wala code chalega...
