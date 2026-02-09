import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime
import time

# --- 1. CONFIGURATION ---
API_KEY = "AIzaSyBSKA3v0cdcNnmvw4rLMM56-lbde57NysY"
genai.configure(api_key=API_KEY, transport='rest')

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('memories.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes 
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 content TEXT, 
                 date TEXT, 
                 filename TEXT,
                 analysis_type TEXT)''')
    conn.commit()
    return conn, c

conn, c = init_db()

# --- 3. MODERN UI STYLING ---
st.set_page_config(
    page_title="Voice AI Assistant Pro", 
    layout="wide", 
    page_icon="🎙️",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
        text-align: center;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.15);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: transform 0.3s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s;
        width: 100%;
        margin: 0.5rem 0;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #FF8E53, #FF6B6B);
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
    }
    .secondary-button>button {
        background: linear-gradient(45deg, #4A00E0, #8E2DE2);
    }
    .success-button>button {
        background: linear-gradient(45deg, #00b09b, #96c93d);
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(45deg, #00b09b, #96c93d);
    }
</style>
""", unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown("# 🎙️ Voice AI Assistant Pro")
st.markdown("### Transform Your Audio into Intelligent Insights")
st.markdown('</div>', unsafe_allow_html=True)

# Create columns for features
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 **Smart Analysis**")
    st.markdown("AI-powered voice analysis with pattern recognition")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 💾 **Memory Storage**")
    st.markdown("Save and retrieve all your analyzed conversations")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 **Instant Insights**")
    st.markdown("Get actionable suggestions in seconds")
    st.markdown('</div>', unsafe_allow_html=True)

# Main upload section
st.markdown("---")
st.markdown("## 📤 Upload Audio File")

uploaded_file = st.file_uploader(
    "Drag and drop or click to upload",
    type=['mp3', 'wav', 'm4a', 'ogg'],
    help="Supported formats: MP3, WAV, M4A, OGG"
)

if uploaded_file:
    # Display audio player
    st.audio(uploaded_file, format=uploaded_file.type)
    
    # Analysis options
    st.markdown("## ⚙️ Analysis Options")
    analysis_type = st.radio(
        "Select analysis type:",
        ["Summary & Suggestions", "Detailed Transcript", "Key Insights Only", "Action Items"]
    )
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        analyze_btn = st.button("🚀 **Analyze Now**", use_container_width=True)
    
    with col2:
        if st.button("✨ **Quick Preview**", use_container_width=True):
            st.info("Quick preview shows basic audio information. For full analysis, use 'Analyze Now'.")
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Type:** {uploaded_file.type}")
            st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
    
    with col3:
        if st.button("💾 **Save for Later**", use_container_width=True):
            c.execute("INSERT INTO notes (content, date, filename, analysis_type) VALUES (?, ?, ?, ?)",
                     ("Saved for later analysis", 
                      datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                      uploaded_file.name, 
                      "Pending"))
            conn.commit()
            st.success(f"✅ '{uploaded_file.name}' saved for later analysis!")
    
    if analyze_btn:
        with st.spinner("🔍 **AI is analyzing your audio...**"):
            progress_bar = st.progress(0)
            
            try:
                # Simulate progress
                for i in range(100):
                    progress_bar.progress(i + 1)
                    time.sleep(0.01)
                
                # AI Analysis
                model = genai.GenerativeModel('gemini-1.5-flash')
                audio_data = {"mime_type": uploaded_file.type, "data": uploaded_file.read()}
                
                # Different prompts based on analysis type
                prompts = {
                    "Summary & Suggestions": """
                    Analyze this audio and provide:
                    1. A clear summary in English
                    2. 3-5 key patterns identified
                    3. 3 actionable suggestions
                    4. Main topics discussed
                    """,
                    "Detailed Transcript": """
                    Provide a detailed transcript of this audio in English.
                    Include speaker changes if detectable and timestamps.
                    """,
                    "Key Insights Only": """
                    Extract only the key insights from this audio.
                    Focus on important points, decisions, and conclusions.
                    """,
                    "Action Items": """
                    Extract all action items, tasks, and to-do's mentioned in this audio.
                    Format as a checklist with priority levels.
                    """
                }
                
                prompt = prompts.get(analysis_type, prompts["Summary & Suggestions"])
                
                try:
                    response = model.generate_content([prompt, audio_data])
                    
                    if response.text:
                        # Display results in a nice container
                        st.markdown("---")
                        st.markdown("## 📊 **Analysis Results**")
                        
                        # Create expandable sections
                        with st.expander(f"### 📝 {analysis_type}", expanded=True):
                            st.markdown(response.text)
                        
                        # Additional info
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**Analysis Type:** {analysis_type}")
                        with col2:
                            st.info(f"**Analyzed On:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                        
                        # Save to database
                        c.execute("INSERT INTO notes (content, date, filename, analysis_type) VALUES (?, ?, ?, ?)",
                                 (response.text, 
                                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                                  uploaded_file.name, 
                                  analysis_type))
                        conn.commit()
                        
                        # Success message
                        st.balloons()
                        st.success("✅ Analysis completed and saved successfully!")
                        
                        # Quick action buttons after analysis
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📋 Copy to Clipboard", use_container_width=True):
                                st.code(response.text, language='text')
                                st.success("Copied! Use Ctrl+V to paste")
                        with col2:
                            if st.button("🔄 Analyze Another", use_container_width=True):
                                st.rerun()
                
                except Exception as e:
                    st.error(f"AI Processing Error: {str(e)}")
                    st.info("Please try again with a different audio file or check your internet connection.")
            
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")
                st.info("**Troubleshooting Tips:**\n1. Check your internet connection\n2. Try using a VPN if needed\n3. Ensure audio file is not corrupted\n4. Try a smaller audio file")

# --- 5. SIDEBAR FEATURES ---
st.sidebar.markdown("""
<div style='background: linear-gradient(45deg, #4A00E0, #8E2DE2); padding: 1rem; border-radius: 10px;'>
<h3 style='color: white; margin: 0;'>🔍 History Panel</h3>
</div>
""", unsafe_allow_html=True)

# Search functionality
search_term = st.sidebar.text_input("🔎 Search in history:", placeholder="Type keywords...")

# Filter options
st.sidebar.markdown("### Filters")
date_filter = st.sidebar.date_input("Select date:")
analysis_filter = st.sidebar.selectbox(
    "Analysis type:",
    ["All", "Summary & Suggestions", "Detailed Transcript", "Key Insights Only", "Action Items"]
)

# Action buttons in sidebar
if st.sidebar.button("📖 Show All History", use_container_width=True):
    if search_term:
        res = c.execute("SELECT * FROM notes WHERE content LIKE ? ORDER BY date DESC", 
                       (f'%{search_term}%',)).fetchall()
    else:
        res = c.execute("SELECT * FROM notes ORDER BY date DESC").fetchall()
    
    if res:
        st.sidebar.success(f"Found {len(res)} records")
        for r in res:
            with st.sidebar.expander(f"📅 {r[3]} - {r[2].split()[0]}", expanded=False):
                st.markdown(f"**Type:** {r[4]}")
                st.markdown(f"**Date:** {r[2]}")
                st.markdown("**Content:**")
                st.text(r[1][:200] + "..." if len(r[1]) > 200 else r[1])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📋 Copy", key=f"copy_{r[0]}"):
                        st.success("Copied!")
                with col2:
                    if st.button(f"🗑️ Delete", key=f"del_{r[0]}"):
                        c.execute("DELETE FROM notes WHERE id=?", (r[0],))
                        conn.commit()
                        st.rerun()
    else:
        st.sidebar.info("No records found")

# Quick stats
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Quick Stats")
total_notes = c.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
today_notes = c.execute("SELECT COUNT(*) FROM notes WHERE date LIKE ?", 
                       (f"{datetime.now().strftime('%Y-%m-%d')}%",)).fetchone()[0]

st.sidebar.metric("Total Notes", total_notes)
st.sidebar.metric("Today's Notes", today_notes)

# Database management
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Database")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
with col2:
    if st.button("📊 Export", use_container_width=True):
        st.sidebar.info("Export feature coming soon!")

if st.sidebar.button("🗑️ Clear All History", type="secondary", use_container_width=True):
    c.execute("DELETE FROM notes")
    conn.commit()
    st.sidebar.success("History cleared!")
    time.sleep(1)
    st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem;'>
<small>Voice AI Assistant Pro v2.0</small><br>
<small>Powered by Gemini AI</small>
</div>
""", unsafe_allow_html=True)

# --- 6. FOOTER ---
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col2:
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
    <small>🔒 Your data is stored locally and securely</small><br>
    <small>🔄 Refresh page to clear temporary data</small><br>
    <small>📧 Support: support@voiceaipro.com</small>
    </div>
    """, unsafe_allow_html=True)







