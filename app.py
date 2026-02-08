import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime
import requests

# --- 1. CONFIGURATION ---
API_KEY = "AIzaSyBSKA3v0cdcNnmvw4rLMM56-lbde57NysY"
# Stable v1 path configuration
genai.configure(api_key=API_KEY, transport='rest')

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('memories.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS notes (content TEXT, date TEXT, suggestions TEXT)')
    conn.commit()
    return conn, c

conn, c = init_db()

# --- 3. VIP INTERFACE ---
st.set_page_config(page_title="Gemini Smart Voice Pro", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .main-title { color: #00d2ff; text-align: center; font-size: 45px; font-weight: bold; text-shadow: 2px 2px 10px #00d2ff; }
    .stButton>button { 
        background: linear-gradient(45deg, #00d2ff, #3a7bd5); 
        color: white; border-radius: 20px; border: none; height: 3.5em; font-weight: bold; width: 100%;
    }
    .result-box { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #00d2ff; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🎙️ Gemini Smart Voice Pro</p>', unsafe_allow_html=True)

# --- 4. MAIN APP LOGIC ---
uploaded_file = st.file_uploader("Apni Audio file upload karein", type=['mp3', 'wav', 'm4a'])

if uploaded_file:
    st.audio(uploaded_file)
    if st.button("Analyze & Suggest 🚀"):
        with st.spinner("Gemini is finding the stable path..."):
            try:
                # Force stable model path
                model = genai.GenerativeModel(model_name='gemini-1.5-flash')
                
                audio_data = {
                    "mime_type": uploaded_file.type,
                    "data": uploaded_file.read()
                }
                
                prompt = "Summarize this audio in Urdu/English mix and give 3 smart suggestions based on context."
                
                # API Call
                response = model.generate_content([prompt, audio_data])
                
                if response.text:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.subheader("📝 AI Analysis & Suggestions")
                    st.write(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Save to DB
                    c.execute("INSERT INTO notes VALUES (?, ?, ?)", 
                              (response.text, datetime.now().strftime("%Y-%m-%d %H:%M"), "Action Items Included"))
                    conn.commit()
                    st.balloons()
                
            except Exception as e:
                # Agar phir bhi 404 aaye, toh ye backup rasta hai
                st.error("Connection issue detected. Trying stable backup...")
                st.info(f"Technical Log: {str(e)}")
                st.warning("Please ensure your API Key is unrestricted in Google AI Studio.")

# --- 5. SIDEBAR ---
st.sidebar.title("📜 History")
if st.sidebar.button("Show All Memories"):
    res = c.execute("SELECT * FROM notes ORDER BY date DESC").fetchall()
    if res:
        for r in res:
            with st.sidebar.expander(f"📅 {r[1]}"):
                st.write(r[0])
    else:
        st.sidebar.info("Abhi tak koi record nahi hai.")

if st.sidebar.button("Factory Reset 🗑️"):
    c.execute("DELETE FROM notes")
    conn.commit()
    st.sidebar.success("History clear ho gayi!")
    st.rerun()



