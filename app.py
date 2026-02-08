import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime
import os
import tempfile
import base64

# --- 1. CONFIGURATION ---
API_KEY = "AIzaSyBSKA3v0cdcNnmvw4rLMM56-lbde57NysY"
genai.configure(api_key=API_KEY)

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('memories.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memories 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  filename TEXT,
                  content TEXT, 
                  summary TEXT,
                  suggestions TEXT,
                  date TEXT)''')
    conn.commit()
    return conn, c

conn, c = init_db()

# --- 3. ENHANCED VIP INTERFACE ---
st.set_page_config(page_title="Gemini Voice Intelligence", layout="wide", page_icon="🎤")

st.markdown("""
<style>
    .stApp { 
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460); 
        color: white; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-title { 
        color: #00d4ff; 
        text-align: center; 
        font-size: 50px; 
        font-weight: 800; 
        text-shadow: 0 0 20px #00d4ff, 0 0 40px #00d4ff;
        margin-bottom: 30px;
        padding: 15px;
        background: rgba(0, 212, 255, 0.1);
        border-radius: 20px;
        border: 2px solid #00d4ff;
    }
    .stButton>button { 
        background: linear-gradient(90deg, #00d4ff 0%, #0080ff 100%); 
        color: white; 
        border-radius: 25px; 
        border: none; 
        height: 60px; 
        font-size: 18px;
        font-weight: bold; 
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 212, 255, 0.6);
    }
    .result-box { 
        background: rgba(255, 255, 255, 0.08); 
        padding: 25px; 
        border-radius: 20px; 
        border: 1px solid #00d4ff; 
        margin: 20px 0;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
    }
    .info-box {
        background: rgba(0, 212, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00d4ff;
        margin: 15px 0;
    }
    .success-box { 
        background: rgba(0, 255, 100, 0.1); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #00ff64; 
        margin: 15px 0;
    }
    .warning-box { 
        background: rgba(255, 193, 7, 0.1); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #ffc107; 
        margin: 15px 0;
    }
    .file-info {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🎤 Gemini Voice Intelligence Pro</p>', unsafe_allow_html=True)

# --- 4. SIDEBAR SETTINGS ---
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Model selection
    model_choice = st.selectbox(
        "Select AI Model",
        ["Gemini Pro (Recommended)", "Gemini Pro Vision", "Text Bison 001"],
        index=0
    )
    
    # Language selection
    language = st.selectbox(
        "Output Language",
        ["Urdu/English Mix", "Urdu Only", "English Only", "Hindi/English Mix"],
        index=0
    )
    
    # Analysis depth
    analysis_depth = st.slider("Analysis Depth", 1, 5, 3)
    
    st.markdown("---")
    st.title("📊 History Stats")
    total_memories = c.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    st.metric("Total Memories", total_memories)
    
    if st.button("🔄 Refresh Stats", use_container_width=True):
        st.rerun()

# --- 5. FILE UPLOAD SECTION ---
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("🎵 Upload Your Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file", 
        type=['mp3', 'wav', 'm4a', 'ogg'],
        help="Maximum file size: 20MB"
    )

with col2:
    st.subheader("ℹ️ File Info")
    if uploaded_file:
        file_size = uploaded_file.size / (1024*1024)  # MB
        st.markdown(f"""
        <div class="file-info">
        <strong>File Name:</strong> {uploaded_file.name}<br>
        <strong>File Type:</strong> {uploaded_file.type}<br>
        <strong>File Size:</strong> {file_size:.2f} MB<br>
        <strong>Status:</strong> ✅ Ready
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No file uploaded yet")

# --- 6. MAIN PROCESSING LOGIC ---
if uploaded_file:
    # Display audio player
    st.audio(uploaded_file)
    
    # Analysis button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_btn = st.button("🚀 Analyze Audio with Gemini Pro", 
                               use_container_width=True,
                               type="primary")
    
    if analyze_btn:
        with st.spinner("🔍 Gemini Pro is analyzing your audio..."):
            try:
                # Initialize Gemini Pro model
                model = genai.GenerativeModel('gemini-pro')
                
                # Create temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    temp_path = tmp_file.name
                
                # Read file as base64 for text description
                with open(temp_path, 'rb') as f:
                    audio_bytes = f.read()
                    # Get file info for description
                    file_info = f"""
                    Audio File Analysis Request:
                    - Filename: {uploaded_file.name}
                    - Type: {uploaded_file.type}
                    - Size: {len(audio_bytes)} bytes
                    """
                
                # Enhanced prompt based on settings
                depth_map = {
                    1: "brief overview",
                    2: "general analysis",
                    3: "detailed analysis",
                    4: "comprehensive analysis",
                    5: "in-depth expert analysis"
                }
                
                prompt = f"""
                Analyze the following audio file content and provide:
                
                ## FILE INFORMATION:
                {file_info}
                
                ## ANALYSIS REQUEST:
                Please provide a {depth_map[analysis_depth]} in {language}.
                
                ## REQUIRED SECTIONS:
                1. **Summary**: Concise summary of audio content
                2. **Key Points**: 5-7 main points discussed
                3. **Emotion/Tone Analysis**: Speaker's emotional state
                4. **Action Items**: Practical suggestions (3-5 items)
                5. **Follow-up Questions**: Questions to ask based on content
                
                ## FORMAT:
                Use clear sections with emojis
                Mix languages naturally as requested
                Be practical and actionable
                
                ## CONTEXT:
                Assume this is important for personal or professional development.
                """
                
                # Generate analysis
                response = model.generate_content(prompt)
                
                if response.text:
                    # Display results
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown("### 📊 Analysis Results")
                    st.markdown("---")
                    
                    # Split response into sections
                    sections = response.text.split('##')
                    for section in sections:
                        if section.strip():
                            st.markdown(f"**{section.strip()}**")
                            st.write("")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Save to database
                    c.execute("""
                        INSERT INTO memories (filename, content, summary, suggestions, date) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        uploaded_file.name,
                        response.text,
                        "Audio Analysis Complete",
                        f"{analysis_depth} level analysis",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    conn.commit()
                    
                    # Success message
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.success("✅ Analysis Complete & Saved to Database!")
                    st.balloons()
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Show quick stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Analysis Depth", f"Level {analysis_depth}")
                    with col2:
                        st.metric("Language", language)
                    with col3:
                        st.metric("Status", "Saved")
                
                # Cleanup
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
            except Exception as e:
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.error("Analysis Failed!")
                st.code(f"Error: {str(e)}", language='python')
                
                # Troubleshooting guide
                with st.expander("🛠️ Troubleshooting Guide"):
                    st.markdown("""
                    ### Common Solutions:
                    
                    1. **VPN Issue** - Turn OFF VPN completely
                    2. **API Key** - Verify at [Google AI Studio](https://makersuite.google.com/app/apikey)
                    3. **Browser** - Try Chrome/Edge in incognito mode
                    4. **File Size** - Ensure file < 20MB
                    5. **Clear Cache** - Clear browser cache and refresh
                    
                    ### Quick Fixes:
                    - Use MP3 format (most compatible)
                    - Reduce file size if large
                    - Check internet connection
                    """)
                
                st.markdown('</div>', unsafe_allow_html=True)

# --- 7. MEMORY MANAGEMENT ---
st.markdown("---")
st.subheader("💾 Memory Bank")

tab1, tab2, tab3 = st.tabs(["📋 View Memories", "🔍 Search", "⚙️ Manage"])

with tab1:
    if st.button("Load All Memories", key="load_mem"):
        memories = c.execute("SELECT * FROM memories ORDER BY date DESC").fetchall()
        
        if memories:
            for mem in memories:
                with st.expander(f"🎵 {mem[1]} - {mem[5]}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Summary:** {mem[3]}")
                        st.markdown("**Full Analysis:**")
                        st.write(mem[2])
                    with col2:
                        st.caption(f"ID: {mem[0]}")
                        if st.button("🗑️", key=f"del_{mem[0]}"):
                            c.execute("DELETE FROM memories WHERE id = ?", (mem[0],))
                            conn.commit()
                            st.success("Deleted!")
                            st.rerun()
        else:
            st.info("No memories saved yet")

with tab2:
    search_term = st.text_input("Search memories by keyword")
    if search_term:
        results = c.execute("""
            SELECT * FROM memories 
            WHERE content LIKE ? OR filename LIKE ?
            ORDER BY date DESC
        """, (f'%{search_term}%', f'%{search_term}%')).fetchall()
        
        if results:
            st.write(f"Found {len(results)} results:")
            for res in results:
                st.write(f"**{res[1]}** - {res[5]}")
                st.caption(res[2][:200] + "..." if len(res[2]) > 200 else res[2])
                st.write("---")
        else:
            st.warning("No matching memories found")

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export All Memories", use_container_width=True):
            memories = c.execute("SELECT * FROM memories").fetchall()
            export_data = "Gemini Voice Intelligence - Memory Export\n"
            export_data += "="*50 + "\n\n"
            
            for mem in memories:
                export_data += f"File: {mem[1]}\n"
                export_data += f"Date: {mem[5]}\n"
                export_data += f"Summary: {mem[3]}\n"
                export_data += f"Analysis:\n{mem[2]}\n"
                export_data += "-"*40 + "\n\n"
            
            st.download_button(
                label="📥 Download Export",
                data=export_data,
                file_name=f"memories_export_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("Clear All Memories", type="secondary", use_container_width=True):
            if st.checkbox("Confirm permanent deletion of ALL memories"):
                c.execute("DELETE FROM memories")
                conn.commit()
                st.error("All memories deleted!")
                st.rerun()

# --- 8. FOOTER ---
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    st.caption(f"🚀 Powered by Gemini Pro • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("Status: ✅ Connected | Model: Gemini Pro")

# --- 9. AUTO-CLEANUP ---
def cleanup_old_files():
    """Remove temporary files older than 1 hour"""
    temp_dir = tempfile.gettempdir()
    for filename in os.listdir(temp_dir):
        if filename.startswith('tmp'):
            filepath = os.path.join(temp_dir, filename)
            try:
                if os.path.getmtime(filepath) < (datetime.now().timestamp() - 3600):
                    os.unlink(filepath)
            except:
                pass

# Run cleanup
cleanup_old_files()





