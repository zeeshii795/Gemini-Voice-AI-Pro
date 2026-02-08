import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime

# --- 1. CONFIGURATION (Stable v1 API) ---
API_KEY = "AIzaSyBSKA3v0cdcNnmvw4rLMM56-lbde57NysY"
# Stable transport aur API setup
genai.configure(api_key=API_KEY, transport='rest')

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('memories.db', check_same_thread=False)
    c = conn.cursor()
    # Suggestions column ke saath table
    c.execute('CREATE TABLE IF NOT EXISTS notes (content TEXT, date TEXT, suggestions TEXT)')
    conn.commit()
    return conn, c

conn, c = init_db()

# --- 3. VIP INTERFACE STYLING ---
st.set_page_config(page_title="Gemini Voice AI Pro", layout="wide", page_icon="🎙️")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }
    .main-title {
        font-size: 45px;
        font-weight: bold;
        text-align: center;
        color: #00d2ff;
        text-shadow: 2px 2px 15px rgba(0, 210, 255, 0.5);
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #00d2ff, #3a7bd5);
        color: white;
        border-radius: 15px;
        border: none;
        height: 3.5em;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(0, 210, 255, 0.4);
    }
    .sidebar .sidebar-content {
        background: rgba(0, 0, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🎙️ Gemini Smart Voice Pro</p>', unsafe_allow_html=True)

# --- 4. MAIN UI ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📥 Upload Audio")
    uploaded_file = st.file_uploader("MP3, WAV, or M4A file select karein", type=['mp3', 'wav', 'm4a'])

    if uploaded_file:
        st.audio(uploaded_file)
        if st.button("Analyze & Generate Suggestions 🚀"):
            with st.spinner("Gemini is analyzing patterns..."):
                try:
                    # Model selection (Stable)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    audio_data = {
                        "mime_type": uploaded_file.type,
                        "data": uploaded_file.read()
                    }
                    
                    # VIP Prompt for Pattern Suggestions
                    prompt = "Summarize this audio in Urdu/English mix. Then, provide 3-5 smart suggestions or next steps based on the speaker's tone and content."
                    
                    response = model.generate_content([prompt, audio_data])
                    
                    st.markdown("### ✨ AI Analysis & Suggestions")
                    st.info(response.text)
                    
                    # Save to Database
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    c.execute("INSERT INTO notes VALUES (?, ?, ?)", (response.text, timestamp, "Pattern Identified"))
                    conn.commit()
                    st.balloons()
                except Exception as e:
                    st.error(f"API Error: {e}")
                    st.warning("Tip: Check your API key or use a VPN if the issue persists.")

with col2:
    st.subheader("📋 App Features")
    st.write("✅ Audio Transcription")
    st.write("✅ Smart Summarization")
    st.write("✅ Actionable Suggestions")
    st.write("✅ Persistent History")
    
    if st.button("Clear Screen 🧹"):
        st.rerun()

# --- 5. SIDEBAR HISTORY ---
st.sidebar.title("📜 Saved Memories")
if st.sidebar.button("Show All History"):
    try:
        res = c.execute("SELECT * FROM notes ORDER BY date DESC").fetchall()
        if res:
            for r in res:
                with st.sidebar.expander(f"📅 {r[1]}"):
                    st.write(r[0])
        else:
            st.sidebar.info("No memories found.")
    except Exception as db_e:
        st.sidebar.error("Database structure updated. Please click 'Factory Reset'.")

if st.sidebar.button("Factory Reset 🗑️"):
    c.execute("DROP TABLE IF EXISTS notes")
    conn.commit()
    st.sidebar.success("Database Reset! App refresh karein.")
    st.rerun()

