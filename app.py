import streamlit as st
import docx
import pandas as pd
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
from streamlit_mic_recorder import speech_to_text
from openai import OpenAI

# --- CONFIGURATION & UI SETUP ---
st.set_page_config(page_title="Smart Notes Engine", page_icon="📝", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { background: linear-gradient(135deg, #6366f1, #a855f7); color: white; border: none; border-radius: 8px; padding: 10px 24px; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4); }
    .stSelectbox, .stTextArea, .stTextInput { background-color: #1e293b !important; border-radius: 8px; }
    .content-block { background-color: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# Initialize session states
if "history" not in st.session_state:
    st.session_state.history = []  
if "current_note" not in st.session_state:
    st.session_state.current_note = None

# =========================================================================
# 🔑 API KEY CONFIGURATION (GROQ PROVIDER)
# Replace with your Groq API Key, or add GROQ_API_KEY to Streamlit Secrets
# =========================================================================
LOCAL_GROQ_KEY = "YOUR_GROQ_API_KEY_HERE"

def call_llm_engine(prompt):
    """Connects to the ultra-fast Groq API cloud engine using updated active models."""
    final_key = LOCAL_GROQ_KEY
    
    # Check Streamlit Cloud Secrets dashboard first
    if "GROQ_API_KEY" in st.secrets:
        final_key = st.secrets["GROQ_API_KEY"]
        
    if not final_key or "YOUR_" in final_key:
        raise ValueError("Missing API Key! Please paste your Groq API key into Streamlit Secrets or Line 30.")
        
    # We use a failover model list so if one model is busy or throttled, it moves to the next
    available_models = ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"]
    last_error = None

    for model_name in available_models:
        try:
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=final_key
            )
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are an expert academic text-processing assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            continue  # If a model fails or is deprecated, try the next one down the line

    raise RuntimeError(f"All Groq models failed. Status log: {str(last_error)}")

# --- DATA EXTRACTION UTILITIES ---
def extract_youtube_transcript(url):
    try:
        video_id = url.split("v=")[1].split("&")[0] if "v=" in url else (url.split("youtu.be/")[1].split("?")[0] if "youtu.be/" in url else url.split("/")[-1])
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t['text'] for t in transcript_list])
    except Exception as e:
        return f"Error extracting YouTube transcript: {str(e)}"

def extract_pdf_text(file):
    reader = PdfReader(file)
    return "".join([page.extract_text() + "\n" for page in reader.pages])

def extract_docx_text(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# --- SIDEBAR: NAVIGATION & HISTORY ---
with st.sidebar:
    st.title("📝 Smart Notes")
    if st.button("➕ Generate New Notes"):
        st.session_state.current_note = None
        st.rerun()
        
    st.markdown("---")
    st.subheader("📚 Saved Notebooks")
    if not st.session_state.history:
        st.caption("No summaries created yet.")
    else:
        for idx, item in enumerate(reversed(st.session_state.history)):
            real_idx = len(st.session_state.history) - 1 - idx
            button_label = f"📖 {item['title']}" if st.session_state.current_note == real_idx else f"📄 {item['title']}"
            if st.button(button_label, key=f"hist_{real_idx}"):
                st.session_state.current_note = real_idx
                st.rerun()

# --- MAIN WORKSPACE MULTIPLEXER ---
if st.session_state.current_note is not None and st.session_state.current_note < len(st.session_state.history):
    idx = st.session_state.current_note
    
    t_col1, t_col2 = st.columns([5, 1])
    with t_col1:
        new_title = st.text_input("✏️ Notebook Title / Topic Name:", value=st.session_state.history[idx]['title'])
        st.session_state.history[idx]['title'] = new_title
    with t_col2:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Delete", key="delete_note_btn"):
            st.session_state.history.pop(idx)
            st.session_state.current_note = None
            st.rerun()
            
    st.markdown("---")
    
    # --- DISPLAY PANELS ---
    st.markdown('<div class="content-block">', unsafe_allow_html=True)
    st.subheader("📝 Generated Study Content (Editable)")
    edited_notes = st.text_area("Notes block:", value=st.session_state.history[idx]['notes'], height=250, key="edit_notes_field")
    st.session_state.history[idx]['notes'] = edited_notes 
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-block">', unsafe_allow_html=True)
    st.subheader("❓ Exam Practice Q&A (Editable)")
    edited_qs = st.text_area("Test assessment sheet:", value=st.session_state.history[idx]['questions'], height=250, key="edit_qs_field")
    st.session_state.history[idx]['questions'] = edited_qs 
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Home View
    st.title("✨ Smart Notes Generator")
    st.caption("Transform any text, files, or your spoken voice into clean, structured notes blocks.")

    h_col1, h_col2 = st.columns(2)
    with h_col1:
        note_format = st.selectbox("Preferred Output Format", ["Bullet Points", "Detailed Paragraphs", "Flashcards (Concept & Definition Pairs)"])
    with h_col2:
        num_questions = st.slider("Number of Exam Questions", 3, 10, 5)

    st.markdown("---")
    input_type = st.radio("Select Input Source:", ["Raw Text", "Voice Notes 🎙️", "YouTube Link", "PDF Document", "Word Document (.docx)"], horizontal=True)
    raw_text = ""
    source_title = "Untitled Summary"

    if input_type == "Raw Text":
        raw_text = st.text_area("Paste material here:", height=150)
        source_title = "Text Snippet" if len(raw_text) > 0 else "Untitled"
    elif input_type == "Voice Notes 🎙️":
        voice_input = speech_to_text(start_prompt="🎙️ Start Recording Voice", stop_prompt="⏹️ Stop & Transcribe", language='en', key='voice_recorder')
        if voice_input:
            st.info(f"📋 **Transcribed:** {voice_input}")
            raw_text = voice_input
            source_title = "Voice Dictation Summary"
    elif input_type == "YouTube Link":
        url = st.text_input("Paste YouTube Video URL:")
        if url:
            with st.spinner("Extracting..."):
                raw_text = extract_youtube_transcript(url)
                source_title = "YouTube Video Summary"
    elif input_type == "PDF Document":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file:
            raw_text = extract_pdf_text(uploaded_file)
            source_title = uploaded_file.name
    elif input_type == "Word Document (.docx)":
        uploaded_file = st.file_uploader("Upload Word Document", type=["docx"])
        if uploaded_file:
            raw_text = extract_docx_text(uploaded_file)
            source_title = uploaded_file.name

    if st.button("🚀 Generate Exam-Ready Notes"):
        if not raw_text.
