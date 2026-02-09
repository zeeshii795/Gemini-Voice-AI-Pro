import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime

# --- 1. CONFIGURATION (Bulletproof Mode) ---
API_KEY = "AIzaSyBSKA3v0cdcNnmvw4rLMM56-lbde57NysY"
# Stable REST transport to avoid 404 errors on Cloud
genai.configure(api_key=API_KEY, transport='rest')

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('memories.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS notes (content TEXT, date TEXT, suggestions TEXT)')
    conn.commit()
    return conn, c

conn, c = init_db()

# --- 3. VIP UI STYLING ---
st.set_page_config(page_title="Gemini Smart Voice Pro", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .main-title { color: #00d2ff; text-align: center; font-size: 40px; font-weight: bold; text-shadow: 2px 2px 10px #00d2ff; }
    .stButton>button { 
        background: linear-gradient(45deg, #00d2ff, #3a7bd5); color: white; border-radius: 20px; font-weight: bold; width: 100%;
    }
    .stInfo { background: rgba(255, 255, 255, 0.1); border: 1px solid #00d2ff; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🎙️ Gemini Smart Voice Pro</p>', unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
uploaded_file = st.file_uploader("Upload Audio Note", type=['mp3', 'wav', 'm4a'])

if uploaded_file:
    st.audio(uploaded_file)
    if st.button("Analyze & Suggest 🚀"):
        with st.spinner("AI is thinking..."):
            try:
                # Stable Model Selection
                model = genai.GenerativeModel('gemini-1.5-flash')
                audio_data = {"mime_type": uploaded_file.type, "data": uploaded_file.read()}
                
                prompt = "Summarize this audio in Urdu/English mix. Identify patterns and give 3 smart suggestions."
                response = model.generate_content([prompt, audio_data])
                
                if response.text:
                    st.subheader("✨ Analysis Result")
                    st.info(response.text)
                    
                    # Save to DB
                    c.execute("INSERT INTO notes VALUES (?, ?, ?)", 
                              (response.text, datetime.now().strftime("%Y-%m-%d %H:%M"), "Success"))
                    conn.commit()
                    st.balloons()
            except Exception as e:
                st.error(f"Connection Issue: {e}")
                st.info("Tip: Try with a VPN if you're in a restricted region.")

# --- 5. SIDEBAR ---
st.sidebar.title("📜 History")
if st.sidebar.button("Show All History"):
    res = c.execute("SELECT * FROM notes ORDER BY date DESC").fetchall()
    for r in res:
        with st.sidebar.expander(f"📅 {r[1]}"):
            st.write(r[0])

if st.sidebar.button("Reset DB 🗑️"):
    c.execute("DELETE FROM notes")
    conn.commit()
    st.sidebar.success("History cleared!")
    st.rerun()






