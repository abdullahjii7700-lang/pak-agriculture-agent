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
WEATHER_KEY = st.secrets["WEATHER_API_KEY"]

# Configure AI Engine
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# Weather Fetcher Function
def get_live_weather(tehsil_name):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={tehsil_name},PK&appid={WEATHER_KEY}&units=metric"
        response = requests.get(url).json()
        if str(response.get("cod")) == "200":
            return {
                "status": "success", 
                "temp": response["main"]["temp"], 
                "condition": response["weather"][0]["main"],
                "rain": response.get("rain", {}).get("3h", 0)
            }
        return {"status": "error", "message": "Location not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

st.write("### 👇 Call Start Karne Ke Liye Button Dabayein")
# Single Call Control UI
audio = mic_recorder(start_prompt="📞 Call Start (Bolna Shuru Karein)", stop_prompt="🛑 Call End (Call Kaatein)", key='call_recorder')

if audio:
    with st.spinner("Call processed ho rahi hai..."):
        audio_data = audio['bytes']
        
        try:
            # Step 1: Pass raw audio bytes directly to Gemini to extract the City/Tehsil
            extraction_prompt = "Suno aur sirf Pakistan ki us tehsil/city ka naam English mein batao jo is audio mein boli gayi hai. respond with just the city name, nothing else."
            city_res = model.generate_content([
                extraction_prompt,
                {"mime_type": "audio/wav", "data": audio_data}
            ])
            extracted_city = city_res.text.strip()
            
            # Step 2: Live Weather Check behind the scenes based on extracted city
            weather = get_live_weather(extracted_city)
            weather_context = "Unknown Weather"
            if weather["status"] == "success":
                weather_context = f"Temp {weather['temp']}°C, Condition {weather['condition']}, Rain {weather['rain']}mm"
            
            # Step 3: Pure Voice Agent Strict Policy Prompt (Audio + Weather Analysis)
            agent_prompt = f"""
            Aap ek professional Agriculture Call Agent hain. Aapke samne ek kisaan ki audio call hai aur uski city ({extracted_city}) ka live weather data ye hai:
            WEATHER DATA: {weather_context}
            
            STRICT RULES:
            1. Is audio ko dhyan se suno aur kisaan ke masle (crop/pest) ka jawab do.
            2. Agar weather 'Rain' hai ya rain > 0mm hai, toh sakhti se mana karne ke liye bolein: 'Mausam kharab hai, spray hargiz na karein.'
            3. Kapaas (cotton) ki safaid makkhi (whitefly) ke liye 'Diafenthiuron 500WP (200ml per acre)' lazmi batayein.
            4. Jawab sirf 2-3 lines ka short aur natural ho, jaise phone par baat ki jati hai. Roman Urdu mein baat karein.
            """
            
            response = model.generate_content([
                agent_prompt,
                {"mime_type": "audio/wav", "data": audio_data}
            ])
            call_response_text = response.text
            
            st.success(f"📞 Agent Ka Jawab: {call_response_text}")
            
            # Step 4: Convert Answer to Free Audio Voice Note (Text-to-Speech)
            tts = gTTS(text=call_response_text, lang='ur', slow=False)
            tts.save("call_output.mp3")
            
            # Play Voice Immediately like a real call
            st.audio("call_output.mp3", format="audio/mp3", autoplay=True)
            os.remove("call_output.mp3")
            
        except Exception as e:
            st.error(f"Call Drop Error: {str(e)}")
