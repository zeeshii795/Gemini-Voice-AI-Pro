import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime
import os
import tempfile

# --- 1. CONFIGURATION ---
API_KEY = "AIzaSyBSKA3v0cdcNnmvw4rLMM56-lbde57NysY"
# Configure with stable settings
genai.configure(api_key=API_KEY)

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('memories.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  content TEXT, 
                  date TEXT, 
                  suggestions TEXT)''')
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
    .success-box { background: rgba(0, 255, 0, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #00ff00; }
    .error-box { background: rgba(255, 0, 0, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #ff0000; }
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
                # Use stable model (gemini-pro is more widely available)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Save uploaded file to temp location
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    temp_path = tmp_file.name
                
                try:
                    # Upload file to Gemini
                    upload_response = genai.upload_file(temp_path)
                    
                    # Wait for file to be processed
                    import time
                    while upload_response.state.name == "PROCESSING":
                        time.sleep(1)
                        upload_response = genai.get_file(upload_response.name)
                    
                    if upload_response.state.name == "FAILED":
                        st.error("File processing failed. Please try again.")
                    else:
                        # Prepare prompt
                        prompt = """
                        Please analyze this audio and provide:
                        1. A summary in mix of Urdu and English
                        2. 3 practical suggestions based on the audio content
                        3. Key points or action items
                        
                        Format output clearly.
                        """
                        
                        # Generate content using file reference
                        response = model.generate_content([
                            prompt,
                            upload_response
                        ])
                        
                        if response.text:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.subheader("📝 AI Analysis & Suggestions")
                            st.write(response.text)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Save to DB
                            c.execute("INSERT INTO notes (content, date, suggestions) VALUES (?, ?, ?)", 
                                      (response.text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "3 suggestions included"))
                            conn.commit()
                            
                            st.markdown('<div class="success-box">✅ Analysis completed and saved to database!</div>', unsafe_allow_html=True)
                            st.balloons()
                
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                
            except Exception as e:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error("Connection issue detected!")
                st.write(f"Error details: {str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Try alternative model if gemini-1.5-flash fails
                st.info("Trying alternative model...")
                try:
                    alternative_model = genai.GenerativeModel('gemini-pro')
                    
                    # Simple text-based fallback
                    prompt = f"Analyze audio content conceptually. This is for an audio file about: {uploaded_file.name}. Provide summary and suggestions in Urdu/English mix."
                    response = alternative_model.generate_content(prompt)
                    
                    if response.text:
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        st.subheader("📝 Fallback Analysis (Text-based)")
                        st.write(response.text)
                        st.markdown('</div>', unsafe_allow_html=True)
                except:
                    st.error("""
                    Please check:
                    1. VPN is TURNED OFF completely
                    2. API Key is valid and has Gemini API enabled
                    3. Refresh the page
                    4. Use Chrome/Edge browser
                    """)

# --- 5. SIDEBAR ---
st.sidebar.title("📜 History")

# Auto-show recent entries
st.sidebar.subheader("Recent Memories")
res = c.execute("SELECT * FROM notes ORDER BY date DESC LIMIT 5").fetchall()
if res:
    for r in res:
        with st.sidebar.expander(f"📅 {r[2][:16]}"):
            st.write(f"**Content:** {r[1][:200]}..." if len(r[1]) > 200 else f"**Content:** {r[1]}")
else:
    st.sidebar.info("Abhi tak koi record nahi hai.")

# Clear button with confirmation
if st.sidebar.button("Clear All History 🗑️"):
    if st.sidebar.checkbox("Confirm delete all history?"):
        c.execute("DELETE FROM notes")
        conn.commit()
        st.sidebar.success("History clear ho gayi!")
        st.rerun()

# Export option
if st.sidebar.button("Export History 📥"):
    res = c.execute("SELECT * FROM notes ORDER BY date DESC").fetchall()
    if res:
        export_text = ""
        for r in res:
            export_text += f"\n\nDate: {r[2]}\nContent: {r[1]}\n{'='*50}"
        
        st.sidebar.download_button(
            label="Download History",
            data=export_text,
            file_name=f"memories_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

# --- 6. TROUBLESHOOTING SECTION ---
with st.sidebar.expander("🚨 Troubleshooting"):
    st.write("""
    **Common Issues & Solutions:**
    
    1. **404/Model Not Found Error:**
       - Turn OFF VPN completely
       - Use browser in incognito mode
       - Clear browser cache
    
    2. **API Key Issues:**
       - Ensure API key is enabled at: https://makersuite.google.com/app/apikey
       - Check billing is enabled
    
    3. **Audio File Issues:**
       - Use MP3 format (most reliable)
       - Keep files under 10MB
       - Ensure clear audio quality
    """)

st.sidebar.markdown("---")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")




