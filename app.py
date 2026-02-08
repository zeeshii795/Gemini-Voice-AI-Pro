import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime
import os

# --- 1. CONFIGURATION (Smart Stable Mode) ---
API_KEY = "AIzaSyBSKA3v0cdcNnmvw4rLMM56-lbde57NysY"

# Is line se hum Google ko "Stable Path" par force karte hain
os.environ["GOOGLE_API_USE_MTLS"] = "never" 
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
    h1 { color: #00d2ff; text-align: center; font-weight: bold; text-shadow: 2px 2px 10px #00d2ff; }
    .stButton>button { 
        background: linear-gradient(45deg, #00d2ff, #3a7bd5); 
        color: white; border-radius: 20px; border: none; height: 3.5em; font-weight: bold; width: 100%;
    }
    .stMarkdown { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #00d2ff; }
    .sidebar .sidebar-content { background: rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ Gemini Smart Voice Pro")

# --- 4. MAIN LOGIC ---
uploaded_file = st.file_uploader("Apni Audio file upload karein", type=['mp3', 'wav', 'm4a'])

if uploaded_file:
    st.audio(uploaded_file)
    if st.button("Analyze & Suggest 🚀"):
        with st.spinner("AI is finding the best path to analyze..."):
            try:
                # SMART MODEL SELECTION: Pehle flash, phir flash-latest
                model_name = 'gemini-1.5-flash' 
                model = genai.GenerativeModel(model_name)
                
                audio_data = {"mime_type": uploaded_file.type, "data": uploaded_file.read()}
                prompt = "Summarize this audio in Urdu/English mix and give 3 smart suggestions."
                
                # Direct call
                response = model.generate_content([prompt, audio_data])
                
                if response:
                    st.subheader("📝 Analysis & Suggestions")
                    st.markdown(response.text)
                    
                    c.execute("INSERT INTO notes VALUES (?, ?, ?)", 
                              (response.text, datetime.now().strftime("%Y-%m-%d %H:%M"), "Success"))
                    conn.commit()
                    st.balloons()
                
            except Exception as e:
                # Agar 404 aaye toh alternate rasta
                st.warning("Trying alternate connection path...")
                try:
                    # Alternate rasta without 'models/' prefix
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    response = model.generate_content([prompt, audio_data])
                    st.markdown(response.text)
                except:
                    st.error(f"Technical Block: {e}")
                    st.info("Tip: VPN on karke refresh karein, kabhi kabhi region issue hota hai.")

# --- 5. SIDEBAR ---
st.sidebar.title("📜 Saved Memories")
if st.sidebar.button("Show All History"):
    res = c.execute("SELECT * FROM notes ORDER BY date DESC").fetchall()
    if res:
        for r in res:
            with st.sidebar.expander(f"📅 {r[1]}"):
                st.write(r[0])
    else:
        st.sidebar.info("History empty hai.")

if st.sidebar.button("Factory Reset 🗑️"):
    c.execute("DELETE FROM notes")
    conn.commit()
    st.sidebar.success("Database Reset!")
    st.rerun()


