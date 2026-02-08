import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime

# --- 1. CONFIGURATION (Stable v1 Force) ---
API_KEY = "AIzaSyBSKA3v0cdcNnmvw4rLMM56-lbde57NysY"
# Ye line stable connection ke liye zaroori hai
genai.configure(api_key=API_KEY, transport='rest')

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('memories.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS notes (content TEXT, date TEXT, suggestions TEXT)')
    conn.commit()
    return conn, c

conn, c = init_db()

# --- 3. VIP UI & STYLING ---
st.set_page_config(page_title="Gemini Voice Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    h1 { color: #00d2ff; text-align: center; font-weight: bold; text-shadow: 2px 2px 10px #00d2ff; }
    .stButton>button { 
        background: linear-gradient(45deg, #00d2ff, #3a7bd5); 
        color: white; border-radius: 20px; border: none; height: 3.5em; font-weight: bold; width: 100%;
    }
    .stMarkdown { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #00d2ff; }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ Gemini Smart Voice Pro")

# --- 4. MAIN INTERFACE ---
uploaded_file = st.file_uploader("Apni Audio file upload karein", type=['mp3', 'wav', 'm4a'])

if uploaded_file:
    st.audio(uploaded_file)
    if st.button("Analyze & Suggest 🚀"):
        with st.spinner("Gemini is thinking (Stable Mode)..."):
            try:
                # Force using the stable 1.5-flash model
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                audio_data = {"mime_type": uploaded_file.type, "data": uploaded_file.read()}
                prompt = "Summarize this audio in Urdu/English mix and give 3 smart suggestions."
                
                # API Call using stable settings
                response = model.generate_content([prompt, audio_data])
                
                st.subheader("📝 Analysis & Suggestions")
                st.markdown(response.text)
                
                # Database Save
                c.execute("INSERT INTO notes VALUES (?, ?, ?)", 
                          (response.text, datetime.now().strftime("%Y-%m-%d %H:%M"), "Action Items Included"))
                conn.commit()
                st.balloons()
            except Exception as e:
                st.error(f"API Error: {e}")
                st.info("Mashwara: Agar ab bhi masla hai, toh AI Studio mein API key ki status check karein.")

# --- 5. SIDEBAR (Buttons fix) ---
st.sidebar.title("📜 Past Memories")
if st.sidebar.button("Show All Memories"):
    res = c.execute("SELECT * FROM notes ORDER BY date DESC").fetchall()
    if res:
        for r in res:
            with st.sidebar.expander(f"📅 {r[1]}"):
                st.write(r[0])
    else:
        st.sidebar.info("No saved memories yet.")

if st.sidebar.button("Clear All 🗑️"):
    c.execute("DELETE FROM notes")
    conn.commit()
    st.sidebar.success("History Cleared!")
    st.rerun()
