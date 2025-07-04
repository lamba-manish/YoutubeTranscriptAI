import streamlit as st
import re
import os
import json
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from youtube_utils import YouTubeTranscriptExtractor
from backend.enhanced_chat_handler import EnhancedChatHandler
from dotenv import load_dotenv
load_dotenv()


def generate_flashcard_text(cards):
    """Convert flashcards to formatted text"""
    text = "FLASHCARDS\n\n"
    for i, card in enumerate(cards):
        text += f"Card {i+1} ({card.get('difficulty', 'medium')})\n"
        text += f"Q: {card.get('question', 'No question')}\n"
        text += f"A: {card.get('answer', 'No answer')}\n\n"
    return text

def generate_pdf_content(title, content):
    """Generate PDF content from text"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_para = Paragraph(f"<b>{title}</b>", styles['Title'])
    story.append(title_para)
    story.append(Spacer(1, 12))
    
    # Content
    for line in content.split('\n'):
        if line.strip():
            para = Paragraph(line, styles['Normal'])
            story.append(para)
        story.append(Spacer(1, 6))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_study_guide_text(guide):
    """Convert study guide to formatted text"""
    text = "STUDY GUIDE\n\n"
    
    if guide.get('overview'):
        text += f"OVERVIEW:\n{guide['overview']}\n\n"
    
    if guide.get('learning_objectives'):
        text += "LEARNING OBJECTIVES:\n"
        for obj in guide['learning_objectives']:
            text += f"• {obj}\n"
        text += "\n"
    
    if guide.get('key_concepts'):
        text += "KEY CONCEPTS:\n"
        for concept in guide['key_concepts']:
            if isinstance(concept, dict):
                text += f"• {concept.get('term', 'Unknown')}: {concept.get('definition', 'No definition')}\n"
            else:
                text += f"• {concept}\n"
        text += "\n"
    
    return text

def generate_study_notes_text(notes):
    """Convert study notes to formatted text"""
    text = "QUICK STUDY NOTES\n\n"
    
    if notes.get('summary'):
        text += f"SUMMARY:\n{notes['summary']}\n\n"
    
    if notes.get('key_points'):
        text += "KEY POINTS:\n"
        for point in notes['key_points']:
            text += f"• {point}\n"
        text += "\n"
    
    if notes.get('actionable_items'):
        text += "ACTION ITEMS:\n"
        for item in notes['actionable_items']:
            text += f"✓ {item}\n"
        text += "\n"
    
    return text

def generate_comprehensive_report():
    """Generate a comprehensive report with all available content"""
    report = "COMPREHENSIVE VIDEO ANALYSIS REPORT\n\n"
    
    # Video info
    if st.session_state.get('enhanced_chat_handler') and st.session_state.enhanced_chat_handler.is_video_loaded():
        video_info = st.session_state.enhanced_chat_handler.get_video_info()
        if video_info:
            report += f"VIDEO: {video_info.get('title', 'Unknown Title')}\n"
            report += f"CHANNEL: {video_info.get('channel', 'Unknown Channel')}\n"
            report += f"DURATION: {video_info.get('duration', 'Unknown')}\n\n"
    
    # Add all available content
    if st.session_state.get('video_summary'):
        report += f"VIDEO SUMMARY:\n{st.session_state.video_summary}\n\n"
    
    if st.session_state.get('video_highlights'):
        report += f"HIGHLIGHT REEL:\n{st.session_state.video_highlights}\n\n"
    
    if st.session_state.get('video_mood'):
        report += f"MOOD ANALYSIS:\n{st.session_state.video_mood}\n\n"
    
    if st.session_state.get('study_guide'):
        guide_text = generate_study_guide_text(st.session_state.study_guide)
        report += f"{guide_text}\n"
    
    if st.session_state.get('study_notes'):
        notes_text = generate_study_notes_text(st.session_state.study_notes)
        report += f"{notes_text}\n"
    
    if st.session_state.get('flashcards'):
        flashcard_text = generate_flashcard_text(st.session_state.flashcards)
        report += f"{flashcard_text}\n"
    
    return report

# Page configuration
st.set_page_config(
    page_title="YouTube Transcript Chat AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern responsive CSS with consistent button widths and proper centering
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --primary-bg: #0F0F23;
        --secondary-bg: #1A1A2E;
        --accent-bg: #16213E;
        --primary-text: #FFFFFF;
        --secondary-text: #B8BCC8;
        --accent-color: #FF6B6B;
        --accent-color-rgb: 255, 107, 107;
        --secondary-accent: #4ECDC4;
        --border-color: #2D2D44;
        --hover-color: #3A3A5C;
        --success-color: #06D6A0;
        --warning-color: #FFD60A;
        --error-color: #EF476F;
        --shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        --border-radius: 12px;
        --button-height: 44px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Global app styling */
    .stApp {
        background: linear-gradient(135deg, var(--primary-bg) 0%, var(--secondary-bg) 100%);
        color: var(--primary-text);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
    }
    
    /* Remove default margins and improve spacing */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem;
        }
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: var(--secondary-bg);
        border-right: 1px solid var(--border-color);
    }
    
    /* Header styling with proper centering */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: -0.025em;
        margin: 0 0 1rem 0;
    }
    
    h1 {
        color: var(--accent-color);
        font-size: clamp(2rem, 5vw, 3rem);
        text-align: center;
        background: linear-gradient(135deg, var(--accent-color), var(--secondary-accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
    }
    
    h2 {
        color: var(--primary-text);
        font-size: clamp(1.5rem, 3vw, 2rem);
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: var(--secondary-accent);
        font-size: clamp(1.25rem, 2.5vw, 1.5rem);
    }
    
    /* Consistent button styling with fixed widths */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-color), #FF5252);
        color: var(--primary-text);
        border: none;
        border-radius: var(--border-radius);
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        height: var(--button-height);
        min-width: 140px;
        width: 100%;
        max-width: 300px;
        margin: 0.25rem 0;
        transition: var(--transition);
        box-shadow: var(--shadow);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: var(--transition);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
    }
    
    .stButton > button:hover:before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary button variant */
    .stButton > button[kind="secondary"] {
        background: var(--accent-bg);
        border: 1px solid var(--border-color);
        color: var(--primary-text);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--hover-color);
        border-color: var(--secondary-accent);
        box-shadow: 0 8px 25px rgba(78, 205, 196, 0.3);
    }
    
    /* Button container for consistent centering */
    .stButton {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0.5rem 0;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--accent-bg);
        color: var(--primary-text);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        padding: 12px 16px;
        transition: var(--transition);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--secondary-accent);
        box-shadow: 0 0 0 2px rgba(78, 205, 196, 0.2);
        outline: none;
    }
    
    /* Chat interface styling */
    .stChatMessage {
        background: var(--accent-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        margin: 1rem 0;
        box-shadow: var(--shadow);
        transition: var(--transition);
    }
    
    .stChatMessage:hover {
        border-color: var(--secondary-accent);
    }
    
    .stChatInput > div {
        background: var(--accent-bg);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        overflow: hidden;
    }
    
    .stChatInput input {
        color: var(--primary-text);
        font-family: 'Inter', sans-serif;
        background: transparent;
        border: none;
        padding: 12px 20px;
    }
    
    /* Container and card styling */
    .custom-container {
        background: var(--accent-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
        transition: var(--transition);
    }
    
    .custom-container:hover {
        border-color: var(--secondary-accent);
        transform: translateY(-2px);
    }
    
    /* Metric and info display */
    .stMetric {
        background: var(--accent-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        text-align: center;
    }
    
    .stMetric > div {
        color: var(--primary-text);
    }
    
    .stMetric .metric-label {
        color: var(--secondary-text);
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .stMetric .metric-value {
        color: var(--accent-color);
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    /* Alert and message styling */
    .stSuccess {
        background: rgba(6, 214, 160, 0.1);
        border: 1px solid var(--success-color);
        border-radius: var(--border-radius);
        color: var(--success-color);
        padding: 1rem;
    }
    
    .stError {
        background: rgba(239, 71, 111, 0.1);
        border: 1px solid var(--error-color);
        border-radius: var(--border-radius);
        color: var(--error-color);
        padding: 1rem;
    }
    
    .stWarning {
        background: rgba(255, 214, 10, 0.1);
        border: 1px solid var(--warning-color);
        border-radius: var(--border-radius);
        color: var(--warning-color);
        padding: 1rem;
    }
    
    .stInfo {
        background: rgba(78, 205, 196, 0.1);
        border: 1px solid var(--secondary-accent);
        border-radius: var(--border-radius);
        color: var(--secondary-accent);
        padding: 1rem;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--secondary-accent), #26D0CE);
        color: var(--primary-text);
        border: none;
        border-radius: var(--border-radius);
        font-weight: 500;
        height: var(--button-height);
        min-width: 140px;
        width: 100%;
        max-width: 300px;
        transition: var(--transition);
        box-shadow: var(--shadow);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(78, 205, 196, 0.4);
    }
    
    /* Selectbox and other inputs */
    .stSelectbox > div > div {
        background: var(--accent-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
    }
    
    .stSelectbox > div > div > div {
        color: var(--primary-text);
    }
    
    /* Spinner and loading states */
    .stSpinner > div {
        border-top-color: var(--accent-color);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, var(--accent-color), var(--secondary-accent));
    }
    
    /* Responsive grid system */
    .responsive-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    @media (max-width: 768px) {
        .responsive-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
            margin: 1rem 0;
        }
    }
    
    /* Center content containers */
    .center-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin: 2rem 0;
    }
    
    /* Feature card styling */
    .feature-card {
        background: var(--accent-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        transition: var(--transition);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .feature-card:hover {
        border-color: var(--secondary-accent);
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
    }
    
    .feature-card h3 {
        color: var(--secondary-accent);
        margin-bottom: 1rem;
    }
    
    .feature-card p {
        color: var(--secondary-text);
        flex-grow: 1;
        margin-bottom: 1.5rem;
    }
    
    /* Typography improvements */
    p, li, span {
        color: var(--secondary-text);
        line-height: 1.7;
    }
    
    /* Code styling */
    code {
        background: var(--primary-bg);
        color: var(--secondary-accent);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.875rem;
    }
    
    pre {
        background: var(--primary-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        overflow-x: auto;
    }
    
    /* Divider styling */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 2rem 0;
    }
    
    /* Image styling */
    .stImage > img {
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        transition: var(--transition);
    }
    
    .stImage > img:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
    }
    
    /* Animation for loading states */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--primary-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--hover-color);
    }
    
    /* Ensure proper spacing and alignment */
    .element-container {
        margin: 1rem 0;
    }
    
    /* Video thumbnail styling */
    .video-thumbnail {
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        transition: var(--transition);
        width: 100%;
        max-width: 480px;
        margin: 0 auto;
        display: block;
    }
    
    .video-thumbnail:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
    }
    
    /* Fixed-size video list buttons */
    .stButton > button[data-testid*="video_"] {
        height: 80px !important;
        min-height: 80px !important;
        max-height: 80px !important;
        background: var(--accent-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--border-radius) !important;
        padding: 0.75rem !important;
        transition: var(--transition) !important;
        position: relative !important;
        overflow: hidden !important;
        white-space: pre-wrap !important;
        text-align: left !important;
        line-height: 1.3 !important;
        font-size: 0.85rem !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
    }
    
    .stButton > button[data-testid*="video_"]:hover {
        background: var(--hover-color) !important;
        border-color: var(--accent-color) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Video list item tooltip */
    .video-tooltip {
        position: absolute;
        top: -100%;
        left: 50%;
        transform: translateX(-50%);
        background: var(--primary-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 0.75rem;
        font-size: 0.8rem;
        white-space: nowrap;
        z-index: 1000;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        max-width: 300px;
        white-space: normal;
    }
    
    .stButton > button[data-testid*="video_"]:hover .video-tooltip {
        opacity: 1;
    }
    
    /* Truncate text in fixed-size buttons */
    .video-button-text {
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        width: 100%;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .loading-animation {
        animation: pulse 1.5s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'enhanced_chat_handler' not in st.session_state:
    st.session_state.enhanced_chat_handler = EnhancedChatHandler()
if 'video_loaded' not in st.session_state:
    st.session_state.video_loaded = False
if 'current_video_loaded' not in st.session_state:
    st.session_state.current_video_loaded = False

def extract_video_id(video_id):
    """Validate and return YouTube video ID if it's in correct format"""
    if not video_id:
        return None
    
    # Clean the input (remove whitespace)
    video_id = video_id.strip()
    
    # Validate video ID format (11 characters, alphanumeric + - and _)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        return video_id
    
    return None

def main():
    # Hero section with proper centering
    st.markdown("""
    <div class="center-content">
        <h1>🎬 YouTube Transcript Chat AI</h1>
        <p style="font-size: 1.25rem; color: var(--secondary-text); text-align: center; max-width: 600px;">
            Transform your YouTube watching experience with AI-powered conversations, study guides, and advanced RAG implementation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with responsive design
    with st.sidebar:
        st.markdown("### 📹 Video Input")
        
        # Video ID input with improved styling
        video_input = st.text_input(
            "YouTube Video ID",
            placeholder="dQw4w9WgXcQ",
            help="Enter a YouTube video ID (11 characters)"
        )
        
        # Language preference for transcript extraction
        st.markdown("#### 🌐 Language Preference")
        language_options = {
            "Auto-detect (Recommended)": "auto",
            "English": "en",
            "Hindi": "hi", 
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Portuguese": "pt",
            "Arabic": "ar",
            "Chinese (Simplified)": "zh-cn",
            "Japanese": "ja",
            "Korean": "ko",
            "Russian": "ru",
            "Italian": "it",
            "Turkish": "tr",
            "Thai": "th",
            "Vietnamese": "vi",
            "Indonesian": "id"
        }
        
        selected_language = st.selectbox(
            "Preferred transcript language:",
            options=list(language_options.keys()),
            index=0,
            help="Choose preferred language for transcript extraction. Auto-detect will try multiple languages including auto-generated captions."
        )
        
        # Add info about auto-generated transcripts
        st.markdown("""
        <div style="font-size: 0.8rem; color: var(--secondary-text); margin-top: 0.5rem;">
            💡 <strong>Auto-generated support:</strong> The system will try both manual and auto-generated transcripts in your preferred language, then fall back to translation if needed.
        </div>
        """, unsafe_allow_html=True)
        
        # Primary action button
        col1, col2 = st.columns([1, 1])
        with col1:
            load_btn = st.button("🚀 Load Video", type="primary", use_container_width=True)
        with col2:
            saved_btn = st.button("📋 Saved Videos", type="secondary", use_container_width=True)
        
        # Handle saved videos display
        if saved_btn:
            st.session_state.show_saved_videos = not st.session_state.get('show_saved_videos', False)
        
        # Display saved videos with improved UI
        if st.session_state.get('show_saved_videos', False):
            st.markdown("---")
            st.markdown("### 💾 Saved Videos")
            try:
                available_videos = st.session_state.enhanced_chat_handler.get_available_videos()
                if available_videos:
                    for video in available_videos[:8]:  # Show max 8 in compact list
                        video_id = video['video_id']
                        title = video['title']
                        channel = video['channel']
                        duration = video.get('duration', 'Unknown')
                        
                        # Truncate title for consistent button size
                        truncated_title = title[:35] + '...' if len(title) > 35 else title
                        truncated_channel = channel[:20] + '...' if len(channel) > 20 else channel
                        
                        # Create fixed-size button with truncated text
                        button_text = f"{truncated_title}\n{truncated_channel} • {video_id}"
                        
                        # Single clickable button for entire video info with tooltip
                        button_container = st.container()
                        with button_container:
                            if st.button(
                                button_text,
                                key=f"video_{video_id}",
                                help=f"Full title: {title}\nChannel: {channel}\nDuration: {duration}\nVideo ID: {video_id}",
                                use_container_width=True
                            ):
                                with st.spinner("Loading video..."):
                                    success = st.session_state.enhanced_chat_handler.load_video(video_id)
                                    if success:
                                        st.session_state.current_video_loaded = True
                                        st.session_state.chat_history = []
                                        st.session_state.show_saved_videos = False
                                        st.rerun()
                else:
                    st.info("No saved videos yet")
            except Exception as e:
                st.error(f"Error loading videos: {str(e)}")
        
        # Handle video loading
        if load_btn and video_input:
            video_id = extract_video_id(video_input)
            if video_id:
                try:
                    chat_handler = st.session_state.enhanced_chat_handler
                    selected_lang_code = language_options[selected_language]
                    
                    if chat_handler.db_manager.video_exists(video_id):
                        with st.spinner("Loading from database..."):
                            success = chat_handler.load_video(video_id)
                            if success:
                                st.session_state.current_video_loaded = True
                                st.session_state.chat_history = []
                                st.success("Video loaded successfully!")
                                st.rerun()
                    else:
                        lang_msg = f"Extracting transcript ({selected_language})..." if selected_lang_code != "auto" else "Extracting transcript (auto-detecting language)..."
                        with st.spinner(lang_msg):
                            extractor = YouTubeTranscriptExtractor()
                            video_info = extractor.get_video_info(video_id)
                            
                            # Pass language preference if not auto-detect
                            if selected_lang_code == "auto":
                                transcript = extractor.get_transcript(video_id)
                            else:
                                transcript = extractor.get_transcript(video_id, languages=[selected_lang_code])
                            
                            if transcript:
                                success = chat_handler.load_video(video_id, transcript, video_info)
                                if success:
                                    st.session_state.current_video_loaded = True
                                    st.session_state.chat_history = []
                                    st.success(f"Video loaded and processed in {selected_language}!")
                                    st.rerun()
                            else:
                                st.error(f"Could not extract transcript in {selected_language}. Try selecting 'Auto-detect' or check if the video has captions available.")
                                
                except Exception as e:
                    st.error(f"Error loading video: {str(e)}")
            else:
                st.error("Invalid YouTube video ID")
        elif load_btn:
            st.warning("Please enter a YouTube video ID")
        
        # Video information display with thumbnail
        if st.session_state.current_video_loaded:
            st.markdown("---")
            st.markdown("### 📊 Current Video")
            try:
                video_info = st.session_state.enhanced_chat_handler.get_video_info()
                if video_info:
                    # Display thumbnail if available
                    thumbnail_url = video_info.get('thumbnail')
                    if thumbnail_url:
                        # Create a responsive layout with thumbnail and info
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.markdown(f'<img src="{thumbnail_url}" class="video-thumbnail" style="width: 150px; height: auto;">', unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                            <div style="padding-left: 1rem;">
                                <h4 style="color: var(--secondary-accent); margin-bottom: 0.5rem; line-height: 1.2;">
                                    {video_info.get('title', 'Unknown Title')}
                                </h4>
                                <p style="margin: 0; color: var(--secondary-text); font-size: 0.9rem;">
                                    📺 {video_info.get('channel', 'Unknown Channel')}<br>
                                    ⏱️ {video_info.get('duration', 'Unknown Duration')}<br>
                                    🆔 <code>{video_info.get('video_id', 'Unknown')}</code>
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        # Fallback without thumbnail
                        st.markdown(f"""
                        <div class="custom-container">
                            <h4 style="color: var(--secondary-accent); margin-bottom: 0.5rem;">
                                {video_info.get('title', 'Unknown Title')}
                            </h4>
                            <p style="margin: 0; color: var(--secondary-text); font-size: 0.9rem;">
                                📺 {video_info.get('channel', 'Unknown Channel')}<br>
                                ⏱️ {video_info.get('duration', 'Unknown Duration')}<br>
                                🆔 <code>{video_info.get('video_id', 'Unknown')}</code>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error displaying video info: {str(e)}")
    
    # Main content area with responsive design
    if not st.session_state.current_video_loaded:
        # Welcome screen with feature cards
        st.markdown("""
        <div class="responsive-grid">
            <div class="feature-card">
                <h3>🤖 AI-Powered Chat</h3>
                <p>Have intelligent conversations about any YouTube video using advanced RAG technology with semantic search and context-aware responses.</p>
            </div>
            <div class="feature-card">
                <h3>📚 Study Materials</h3>
                <p>Generate comprehensive study guides, flashcards, and learning paths automatically from video content with AI analysis.</p>
            </div>
            <div class="feature-card">
                <h3>🎯 Smart Analysis</h3>
                <p>Extract key insights, highlight reels, mood analysis, and detailed summaries with timestamp references and citations.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick start guide
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="center-content">
                <h2>🚀 Quick Start</h2>
                <p>Get started in 3 simple steps:</p>
                <ol style="text-align: left; max-width: 400px;">
                    <li>Enter a YouTube video ID or URL in the sidebar</li>
                    <li>Click "Load Video" to process the transcript</li>
                    <li>Start chatting with AI about the video content</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Chat interface with enhanced UI
        st.markdown("## 💬 Chat with AI")
        
        # Chat history display
        if st.session_state.chat_history:
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                else:
                    with st.chat_message("assistant"):
                        st.write(message["content"])
        else:
            st.info("Start a conversation about the video! Ask questions, request summaries, or explore the content.")
        
        # Chat input
        if prompt := st.chat_input("Ask anything about this video..."):
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.enhanced_chat_handler.get_response(
                            prompt, st.session_state.chat_history
                        )
                        st.write(response)
                        
                        # Add assistant response to chat history
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        
                    except Exception as e:
                        error_msg = f"I apologize, but I encountered an error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        
        # Feature buttons with responsive layout
        st.markdown("---")
        st.markdown("### 🛠️ AI Features")
        
        # Create responsive button grid
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📋 Generate Summary", use_container_width=True):
                with st.spinner("Generating summary..."):
                    try:
                        summary = st.session_state.enhanced_chat_handler.get_video_summary()
                        st.session_state.video_summary = summary
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating summary: {str(e)}")
        
        with col2:
            if st.button("✨ Highlight Reel", use_container_width=True):
                with st.spinner("Creating highlights..."):
                    try:
                        highlights = st.session_state.enhanced_chat_handler.get_highlight_reel()
                        st.session_state.video_highlights = highlights
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating highlights: {str(e)}")
        
        with col3:
            if st.button("🎭 Mood Analysis", use_container_width=True):
                with st.spinner("Analyzing mood..."):
                    try:
                        mood = st.session_state.enhanced_chat_handler.get_video_mood_analysis()
                        st.session_state.video_mood = mood
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error analyzing mood: {str(e)}")
        
        with col4:
            if st.button("🧠 Study Guide", use_container_width=True):
                with st.spinner("Creating study guide..."):
                    try:
                        study_guide = st.session_state.enhanced_chat_handler.generate_study_guide()
                        st.session_state.study_guide = study_guide
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating study guide: {str(e)}")
        
        # Display generated content
        if st.session_state.get('video_summary'):
            with st.expander("📋 Video Summary", expanded=False):
                st.write(st.session_state.video_summary)
        
        if st.session_state.get('video_highlights'):
            with st.expander("✨ Highlight Reel", expanded=False):
                st.write(st.session_state.video_highlights)
        
        if st.session_state.get('video_mood'):
            with st.expander("🎭 Mood Analysis", expanded=False):
                st.write(st.session_state.video_mood)
        
        if st.session_state.get('study_guide'):
            with st.expander("🧠 Study Guide", expanded=False):
                study_guide = st.session_state.study_guide
                
                if study_guide.get('learning_objectives'):
                    st.markdown("**Learning Objectives:**")
                    for obj in study_guide['learning_objectives']:
                        st.write(f"• {obj}")
                
                if study_guide.get('key_concepts'):
                    st.markdown("**Key Concepts:**")
                    for concept in study_guide['key_concepts']:
                        if isinstance(concept, dict):
                            st.write(f"• **{concept.get('term', 'Unknown')}**: {concept.get('definition', 'No definition')}")
                        else:
                            st.write(f"• {concept}")
        
        # Additional features row
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗃️ Quick Notes", use_container_width=True):
                with st.spinner("Creating quick notes..."):
                    try:
                        notes = st.session_state.enhanced_chat_handler.generate_study_notes()
                        st.session_state.study_notes = notes
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating notes: {str(e)}")
        
        with col2:
            if st.button("🃏 Flashcards", use_container_width=True):
                with st.spinner("Generating flashcards..."):
                    try:
                        flashcards = st.session_state.enhanced_chat_handler.generate_flashcards(15)
                        st.session_state.flashcards = flashcards
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating flashcards: {str(e)}")
        
        with col3:
            if st.button("📄 Export All", use_container_width=True):
                try:
                    report = generate_comprehensive_report()
                    pdf_content = generate_pdf_content("YouTube Video Analysis Report", report)
                    
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_content,
                        file_name="video_analysis_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
        
        # Display additional content
        if st.session_state.get('study_notes'):
            with st.expander("🗃️ Quick Study Notes", expanded=False):
                notes = st.session_state.study_notes
                if notes.get('summary'):
                    st.markdown(f"**Summary:** {notes['summary']}")
                if notes.get('key_points'):
                    st.markdown("**Key Points:**")
                    for point in notes['key_points']:
                        st.write(f"• {point}")
        
        if st.session_state.get('flashcards'):
            with st.expander("🃏 Flashcards", expanded=False):
                flashcards = st.session_state.flashcards
                for i, card in enumerate(flashcards[:10], 1):  # Show first 10
                    st.markdown(f"**Card {i}** ({card.get('difficulty', 'medium')})")
                    st.markdown(f"**Q:** {card.get('question', 'No question')}")
                    st.markdown(f"**A:** {card.get('answer', 'No answer')}")
                    if i < min(len(flashcards), 10):
                        st.markdown("---")

if __name__ == "__main__":
    main()
