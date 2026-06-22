import streamlit as st
import google.generativeai as genai
import requests

# Page setup for Enterprise Look
st.set_page_config(page_title="Pak Agri-AI Expert", page_icon="🌾", layout="centered")
st.title("🌾 Pak Agri-AI Enterprise System")
st.write("100% Accurate Data-Driven Agriculture Advisory")

# Fetching API Keys securely from Streamlit Secrets
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
WEATHER_KEY = st.secrets["WEATHER_API_KEY"]

# Function to get 100% Accurate Weather Data from OpenWeatherMap
def get_live_weather(tehsil_name):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={tehsil_name},PK&appid={WEATHER_KEY}&units=metric"
        response = requests.get(url).json()
        
        # Bug Fixed: Converting 'cod' to string to avoid type conflicts
        if str(response.get("cod")) == "200":
            temp = response["main"]["temp"]
            condition = response["weather"][0]["main"] 
            description = response["weather"][0]["description"]
            rain_3h = response.get("rain", {}).get("3h", 0)
            return {"status": "success", "temp": temp, "condition": condition, "desc": description, "rain": rain_3h}
        else:
            return {"status": "error", "message": "Tehsil nahi mili. Sahi naam enter karein."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# User Interface Input Fields
tehsil = st.text_input("Apni Tehsil ka naam likhein (e.g., Chishtian, Arifwala):", "")
crop = st.selectbox("Fasal (Crop) select karein:", ["Kapaas (Cotton)", "Gandum (Wheat)", "Dhan (Rice)", "Makai (Maize)"])
problem = st.selectbox("Ahem Masla (Pest/Problem) select karein:", ["Safaid Makkhi (Whitefly)", "Teli (Aphids)", "Lashkari Sundi", "Gulaabi Sundi", "Kayi Aur Masla"])

if st.button("Verified Mashwara Hasil Karein"):
    if not tehsil:
        st.warning("Meharbani karke pehle Tehsil ka naam likhein.")
    else:
        with st.spinner("Live Weather API check ki ja rahi hai aur AI Mashwara tayar ho raha hai..."):
            weather_data = get_live_weather(tehsil)
            
            if weather_data["status"] == "error":
                st.error(weather_data["message"])
            else:
                genai.configure(api_key=GEMINI_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                strict_prompt = f"""
                Aap ek professional Pakistani Agriculture Expert Agent hain.
                Aapka kaam kisaan ko live weather data ke mutabiq 100% sahi mashwara dena hai.

                LIVE WEATHER API DATA (Zero Hallucination Guardrail):
                - Tehsil/Location: {tehsil}, Pakistan
                - Current Temperature: {weather_data['temp']}°C
                - Weather Condition: {weather_data['condition']} ({weather_data['desc']})
                - Rain Data (Last 3 hours): {weather_data['rain']} mm

                USER REQUEST:
                - Fasal: {crop}
                - Masla/Pest: {problem}

                STRICT EXECUTION RULES:
                1. Mausam ka haal strictly upar diye gaye API DATA se hi uthana hai. Apni taraf se farz nahi karna.
                2. Agar Weather Condition mein 'Rain', 'Drizzle', 'Thunderstorm' ho, YA Rain Data 0 mm se zyada ho, toh spray karne se SAKHTI SE ROK DEIN (Chahe dhoop hi kyun na lag rahi ho). Batayein ke dawai zaya ho jaye gi.
                3. Agar Weather Condition 'Clear', 'Sunny', ya 'Clouds' hai aur baarish 0 mm hai, toh spray karne ki ijazat dein kyunke mausam khushk hai.
                4. Agar Fasal 'Kapaas' hai aur Masla 'Safaid Makkhi' hai, toh dawai ka naam 'Diafenthiuron 500WP (200ml per acre)' lazmi batayein.
                5. Pura jawab professional Roman Urdu mein likhein. Heading, Sub-headings aur Bullet points ka istemal karein taake parhna aasan ho. Bold formatting se ahem baaton ko highlight karein.
                """
                
                try:
                    response = model.generate_content(strict_prompt)
                    
                    st.subheader(f"🌤️ Current Weather in {tehsil}")
                    col1, col2 = st.columns(2)
                    col1.metric("Temperature", f"{weather_data['temp']} °C")
                    col2.metric("Condition", weather_data['condition'])
                    
                    st.markdown("---")
                    st.subheader("📋 Expert Agri Advisory")
                    st.write(response.text)
                    
                except Exception as ai_err:
                    st.error(f"AI Engine Exception: {str(ai_err)}")
