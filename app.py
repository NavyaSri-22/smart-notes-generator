import streamlit as st
import docx
import pandas as pd
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
from streamlit_mic_recorder import speech_to_text
from google import genai

# ==========================================
# 🔑 SECURITY: ADD YOUR BACKUP API KEYS HERE
# ==========================================
GEMINI_API_KEYS = [
    "api key"
    "api key"
] 

# --- CONFIGURATION & PREMIUM UI SETUP ---
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

# --- ROTATING ENGINE EXECUTION FUNCTION ---
def call_gemini_with_failover(prompt):
    valid_keys = [k for k in GEMINI_API_KEYS if k and "YOUR_" not in k and len(k) > 10]
    if not valid_keys:
        raise ValueError("Missing API Keys! Please fill out the API keys roster array on Line 12.")
    
    for current_key in valid_keys:
        try:
            client = genai.Client(api_key=current_key)
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text
        except Exception:
            continue
    raise RuntimeError("All configured API Keys failed or ran out of quota limits simultaneously.")

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
    st.markdown("---")
    st.caption("Project Build v11.2 • Strict Data Splitter")

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
    
    # --- INTERACTIVE DIAGRAMS ---
    dot_code = st.session_state.history[idx].get('flowchart', '').strip()
    chart_data = st.session_state.history[idx].get('metrics', [])
    
    if dot_code or chart_data:
        st.subheader("📊 Interactive Diagram Charts")
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            if dot_code and "digraph" in dot_code:
                st.markdown("**Generated Process Flow Chart**")
                try:
                    st.graphviz_chart(dot_code)
                except Exception:
                    st.caption("Flowchart structural layout error.")
                    
        with viz_col2:
            if chart_data and len(chart_data) > 0:
                st.markdown("**Metric Metrics Breakdown**")
                try:
                    df = pd.DataFrame(chart_data)
                    st.bar_chart(df.set_index("Label"))
                except Exception:
                    st.caption("Data matrices chart error.")
        st.markdown("---")
    
    # --- REFINEMENT PANEL ---
    st.subheader("🛠️ Refinement Action Panel")
    ctrl_col1, ctrl_col2 = st.columns(2)
    
    with ctrl_col1:
        st.markdown("**Modify Study Content Format**")
        new_format_choice = st.selectbox("Select New Content Style:", ["Bullet Points", "Detailed Paragraphs", "Flashcards (Concept & Definition Pairs)", "Short Notes Summary"], key="ref_format_selector")
        if st.button("📝 Update & Refine Notes"):
            with st.spinner("🧠 AI rewriting notes..."):
                try:
                    note_prompt = f"Rewrite this material strictly into this requested format: '{new_format_choice}'. Use clear markdown. Material:\n{st.session_state.history[idx]['notes']}"
                    st.session_state.history[idx]['notes'] = call_gemini_with_failover(note_prompt)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
                    
    with ctrl_col2:
        st.markdown("**Generate Brand New Practice Questions**")
        regen_count = st.slider("Select Fresh Question Count:", 3, 15, 5, key="regen_count_slider")
        if st.button("❓ Generate New Questions"):
            with st.spinner("🧠 AI writing unique questions..."):
                try:
                    qs_prompt = f"Generate exactly {regen_count} brand-new questions without duplicating these: {st.session_state.history[idx]['questions']}\nNotes:\n{st.session_state.history[idx]['notes']}"
                    st.session_state.history[idx]['questions'] = call_gemini_with_failover(qs_prompt)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
                    
    st.markdown("---")
    
    # --- TEXT INPUT / CONTENT DISPLAY FIELDS (STRICT SEPARATION) ---
    st.markdown('<div class="content-block">', unsafe_allow_html=True)
    st.subheader("📝 Generated Study Content (Editable)")
    edited_notes = st.text_area("Modify summaries text:", value=st.session_state.history[idx]['notes'], height=250, key="edit_notes_field")
    st.session_state.history[idx]['notes'] = edited_notes 
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-block">', unsafe_allow_html=True)
    st.subheader("❓ Exam Practice Q&A (Editable)")
    edited_qs = st.text_area("Modify test sheet questions:", value=st.session_state.history[idx]['questions'], height=250, key="edit_qs_field")
    st.session_state.history[idx]['questions'] = edited_qs 
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Home View
    st.title("✨ Smart Notes Generator")
    st.caption("Transform any text, files, or your spoken voice into clean, structured notes blocks.")

    h_col1, h_col2 = st.columns(2)
    with h_col1:
        note_format = st.selectbox("Preferred Output Format", ["Bullet Points", "Detailed Paragraphs", "Flashcards (Concept & Definition Pairs)", "Mindmap Structure"])
    with h_col2:
        num_questions = st.slider("Number of Exam Questions", 3, 10, 5)

    enable_diagrams = st.checkbox("🎨 Generate Visual Charts & Diagrams (Uses more API Quota)", value=False)

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
        if not raw_text.strip():
            st.error("❌ Please provide some input material first.")
        else:
            with st.spinner("🧠 Processing your structured segments..."):
                try:
                    # Explicit layout wrapping tags are enforced every time now to fix the splitting bug
                    pipeline_prompt = f"""
                    You are an academic systems assistant. Analyze the source text and split your response into explicit tag sections.
                    
                    [NOTES_BLOCK]
                    Generate comprehensive study notes structured strictly as '{note_format}'. Do not include questions here.
                    [/NOTES_BLOCK]

                    [QUESTIONS_BLOCK]
                    Generate exactly {num_questions} clear exam practice questions. Place the direct answer key text immediately beneath each generated question item.
                    [/QUESTIONS_BLOCK]
                    """
                    
                    if enable_diagrams:
                        pipeline_prompt += """
                        [FLOWCHART_BLOCK]
                        Create a valid Graphviz layout code block mapping the process steps or timelines. Start with 'digraph G {' and close with '}'. Do NOT wrap in backticks.
                        [/FLOWCHART_BLOCK]
                        
                        [METRICS_BLOCK]
                        If there are values, output them strictly as a simple list formatted as Label:Value separated by commas. If none are found, write None.
                        [/METRICS_BLOCK]
                        """
                        
                    pipeline_prompt += f"\n\nSource Material:\n{raw_text[:12000]}"
                    
                    ai_response = call_gemini_with_failover(pipeline_prompt)
                    st.balloons()
                    
                    # Safe explicit tag extract block
                    text_notes = "No notes compiled."
                    text_qs = "No questions compiled."
                    flow_part = ""
                    metrics_list = []
                    
                    if "[NOTES_BLOCK]" in ai_response and "[/NOTES_BLOCK]" in ai_response:
                        text_notes = ai_response.split("[NOTES_BLOCK]")[1].split("[/NOTES_BLOCK]")[0].strip()
                    
                    if "[QUESTIONS_BLOCK]" in ai_response and "[/QUESTIONS_BLOCK]" in ai_response:
                        text_qs = ai_response.split("[QUESTIONS_BLOCK]")[1].split("[/QUESTIONS_BLOCK]")[0].strip()

                    if enable_diagrams:
                        if "[FLOWCHART_BLOCK]" in ai_response and "[/FLOWCHART_BLOCK]" in ai_response:
                            flow_part = ai_response.split("[FLOWCHART_BLOCK]")[1].split("[/FLOWCHART_BLOCK]")[0].strip()
                            flow_part = flow_part.replace("```graphviz", "").replace("```dot", "").replace("```", "").strip()
                        if "[METRICS_BLOCK]" in ai_response and "[/METRICS_BLOCK]" in ai_response:
                            metric_string = ai_response.split("[METRICS_BLOCK]")[1].split("[/METRICS_BLOCK]")[0].strip()
                            if "None" not in metric_string and ":" in metric_string:
                                for pair in metric_string.split(","):
                                    if ":" in pair:
                                        lbl, val = pair.split(":", 1)
                                        try:
                                            metrics_list.append({"Label": lbl.strip(), "Value": float(val.strip().replace("%",""))})
                                        except:
                                            pass

                    st.session_state.history.append({
                        "title": source_title,
                        "notes": text_notes,
                        "questions": text_qs,
                        "flowchart": flow_part,
                        "metrics": metrics_list
                    })
                    st.session_state.current_note = len(st.session_state.history) - 1
                    st.rerun()
                            
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")