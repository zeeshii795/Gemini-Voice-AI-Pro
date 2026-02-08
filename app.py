import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime

# --- CONFIG ---
API_KEY = "AIzaSyBSKA3v0cdcNnmvw4rLMM56-lbde57NysY"
# FORCE STABLE REST TRANSPORT
genai.configure(api_key=API_KEY, transport='rest')

# Database
def init_db():
    conn = sqlite3.connect('memories.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS notes (content TEXT, date TEXT, suggestions TEXT)')
    conn.commit()
    return conn, c

conn, c = init_db()

# --- VIP UI ---
st.set_page_config(page_title="Gemini Voice Pro", layout="wide")
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    h1 { color: #00d2ff; text-align: center; text-shadow: 2px 2px 10px #00d2ff; }
    .stButton>button { background: linear-gradient(45deg, #00d2ff, #3a7bd5); color: white; border-radius: 20px; width: 100%; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ Gemini Smart Voice Pro")

uploaded_file = st.file_uploader("Apni Audio file upload karein", type=['mp3', 'wav', 'm4a'])

if uploaded_file:
    st.audio(uploaded_file)
    if st.button("Analyze & Suggest 🚀"):
        with st.spinner("AI is thinking..."):
            try:
                # USE LATEST STABLE MODEL
                model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
                
                audio_data = {"mime_type": uploaded_file.type, "data": uploaded_file.read()}
                prompt = "Summarize this audio in Urdu/English mix and give 3 smart suggestions."
                
                response = model.generate_content([prompt, audio_data])
                
                st.subheader("📝 Analysis")
                st.success(response.text)
                
                c.execute("INSERT INTO notes VALUES (?, ?, ?)", 
                          (response.text, datetime.now().strftime("%Y-%m-%d %H:%M"), "VIP"))
                conn.commit()
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Tip: Try to refresh the page or check if the API key is active in Google AI Studio.")

# Sidebar History
st.sidebar.title("📜 Past Memories")
if st.sidebar.button("Show All"):
    res = c.execute("SELECT * FROM notes ORDER BY date DESC").fetchall()
    for r in res:
        with st.sidebar.expander(f"📅 {r[1]}"):
            st.write(r[0])
