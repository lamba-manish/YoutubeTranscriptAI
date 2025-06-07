import streamlit as st
import re
import os
import json
from youtube_utils import YouTubeTranscriptExtractor
from backend.enhanced_chat_handler import EnhancedChatHandler

# Page configuration
st.set_page_config(
    page_title="YouTube Transcript Chat AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for YouTube-inspired modern design
st.markdown("""
<style>
    /* Import Roboto font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Main theme colors and styling */
    .stApp {
        background-color: #0F0F0F;
        color: #FFFFFF;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #212121;
        border-right: 1px solid #303030;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #0F0F0F;
    }
    
    /* Title styling */
    h1 {
        color: #FF0000;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Headers */
    h2, h3 {
        color: #FFFFFF;
        font-weight: 500;
    }
    
    /* Sidebar headers */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: #FFFFFF;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #212121;
        color: #FFFFFF;
        border: 1px solid #303030;
        border-radius: 8px;
        font-family: 'Roboto', sans-serif;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #065FD4;
        box-shadow: 0 0 0 1px #065FD4;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #FF0000;
        color: #FFFFFF;
        border: none;
        border-radius: 24px;
        font-weight: 500;
        font-family: 'Roboto', sans-serif;
        transition: all 0.3s ease;
        padding: 0.5rem 1.5rem;
    }
    
    .stButton > button:hover {
        background-color: #CC0000;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255, 0, 0, 0.3);
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background-color: #303030;
        color: #FFFFFF;
        border: 1px solid #AAAAAA;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #404040;
        border-color: #FFFFFF;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #212121;
        border-radius: 12px;
        border: 1px solid #303030;
        margin: 0.5rem 0;
    }
    
    /* Chat input */
    .stChatInput > div > div > div > div {
        background-color: #212121;
        border: 1px solid #303030;
        border-radius: 24px;
    }
    
    .stChatInput input {
        color: #FFFFFF;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: rgba(6, 95, 212, 0.1);
        color: #065FD4;
        border-left: 4px solid #065FD4;
        border-radius: 4px;
    }
    
    .stError {
        background-color: rgba(255, 0, 0, 0.1);
        color: #FF0000;
        border-left: 4px solid #FF0000;
        border-radius: 4px;
    }
    
    .stWarning {
        background-color: rgba(255, 193, 7, 0.1);
        color: #FFC107;
        border-left: 4px solid #FFC107;
        border-radius: 4px;
    }
    
    /* Dividers */
    hr {
        border-color: #303030;
        margin: 1.5rem 0;
    }
    
    /* Markdown text */
    .markdown-text-container {
        color: #AAAAAA;
        line-height: 1.6;
    }
    
    /* Image styling */
    .stImage > img {
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Container styling */
    .stContainer {
        background-color: #212121;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #303030;
        margin: 1rem 0;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #FF0000;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background-color: #065FD4;
        color: #FFFFFF;
        border-radius: 8px;
        font-family: 'Roboto', sans-serif;
    }
    
    .stDownloadButton > button:hover {
        background-color: #0047AB;
    }
    
    /* Column styling */
    .element-container {
        color: #FFFFFF;
    }
    
    /* Metrics and info boxes */
    .metric-container {
        background-color: #212121;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #303030;
    }
    
    /* Custom welcome card */
    .welcome-card {
        background: linear-gradient(135deg, #212121 0%, #303030 100%);
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #404040;
        margin: 1rem 0;
    }
    
    /* Video info card */
    .video-info-card {
        background-color: #212121;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #303030;
        margin: 0.5rem 0;
    }
    
    /* Chat history counter */
    .chat-counter {
        background-color: #303030;
        color: #AAAAAA;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        text-align: center;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        h1 {
            font-size: 2rem;
        }
        
        .welcome-card {
            padding: 1.5rem;
        }
        
        .video-info-card {
            padding: 0.8rem;
        }
    }
    
    /* Loading animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .loading-text {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Hover effects for interactive elements */
    .video-info-card:hover {
        transform: translateY(-2px);
        transition: transform 0.3s ease;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }
    
    .welcome-card:hover {
        transform: translateY(-2px);
        transition: transform 0.3s ease;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-online {
        background-color: #00FF00;
        box-shadow: 0 0 6px #00FF00;
    }
    
    .status-loading {
        background-color: #FFC107;
        box-shadow: 0 0 6px #FFC107;
        animation: pulse 1s ease-in-out infinite;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #212121;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #404040;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #505050;
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

def extract_video_id(url_or_id):
    """Extract YouTube video ID from URL or return ID if already provided"""
    if not url_or_id:
        return None
    
    # If it's already a video ID (11 characters, alphanumeric + - and _)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    # Extract from various YouTube URL formats
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return None

def main():
    # App title with status indicator
    if st.session_state.enhanced_chat_handler.is_video_loaded():
        status_html = '<span class="status-indicator status-online"></span>'
        status_text = "Ready to Chat"
    else:
        status_html = '<span class="status-indicator status-loading"></span>'
        status_text = "Waiting for Video"
    
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='margin-bottom: 0.5rem;'>🎬 YouTube Transcript Chat AI</h1>
        <div style='color: #AAAAAA; font-size: 1rem;'>
            {status_html}{status_text}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for video input and info
    with st.sidebar:
        st.header("📹 Video Input")
        
        # Show available videos button
        if st.button("📋 Show Saved Videos", type="secondary", use_container_width=True):
            st.session_state.show_saved_videos = not st.session_state.get('show_saved_videos', False)
        
        # Display saved videos if requested
        if st.session_state.get('show_saved_videos', False):
            try:
                available_videos = st.session_state.enhanced_chat_handler.get_available_videos()
                if available_videos:
                    st.markdown("### 💾 Saved Videos")
                    for video in available_videos[:8]:  # Show max 8 in sidebar
                        with st.container():
                            # Video info display
                            title_short = video['title'][:30] + "..." if len(video['title']) > 30 else video['title']
                            st.markdown(f"**{title_short}**")
                            st.markdown(f"`{video['video_id']}`")
                            st.markdown(f"*{video['channel']}*")
                            
                            # Load button
                            if st.button(f"Load", key=f"load_{video['video_id']}", use_container_width=True):
                                with st.spinner("Loading..."):
                                    success = st.session_state.enhanced_chat_handler.load_video(video['video_id'])
                                    if success:
                                        st.session_state.current_video_loaded = True
                                        st.session_state.chat_history = []
                                        # Clear previous video features
                                        st.session_state.video_summary = None
                                        st.session_state.video_highlights = None
                                        st.session_state.video_mood = None
                                        st.session_state.show_saved_videos = False
                                        st.rerun()
                            st.divider()
                else:
                    st.info("No saved videos yet")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # Video ID input
        video_input = st.text_input(
            "YouTube Video ID",
            placeholder="dQw4w9WgXcQ",
            help="Enter an 11-character YouTube video ID (found in the URL after v=)"
        )
        
        if st.button("Load Video", type="primary"):
            if video_input:
                # Clean the input and validate it's a proper video ID
                video_id = video_input.strip()
                
                # Basic validation for YouTube video ID format
                if len(video_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                    try:
                        # Check if video already exists in database
                        chat_handler = st.session_state.enhanced_chat_handler
                        
                        if chat_handler.db_manager.video_exists(video_id):
                            # Load from database
                            success = chat_handler.load_video(video_id)
                            if success:
                                st.session_state.current_video_loaded = True
                                st.session_state.chat_history = []  # Reset chat history
                                # Clear previous video features
                                st.session_state.video_summary = None
                                st.session_state.video_highlights = None
                                st.session_state.video_mood = None
                                st.rerun()
                        else:
                            # Extract new transcript
                            with st.spinner("Extracting transcript..."):
                                extractor = YouTubeTranscriptExtractor()
                                video_info = extractor.get_video_info(video_id)
                                transcript = extractor.get_transcript(video_id)
                                
                                if transcript:
                                    # Load and process with enhanced handler
                                    success = chat_handler.load_video(video_id, transcript, video_info)
                                    if success:
                                        st.session_state.current_video_loaded = True
                                        st.session_state.chat_history = []  # Reset chat history
                                        st.rerun()
                                else:
                                    st.error("❌ Could not extract transcript from this video. Make sure the video has captions available.")
                                    
                    except Exception as e:
                        st.error(f"❌ Error loading video: {str(e)}")
                        st.info("💡 Try a different video ID or make sure the video has captions available.")
                else:
                    st.error("❌ Please enter a valid 11-character YouTube video ID")
            else:
                st.warning("⚠️ Please enter a YouTube video ID")
        
        # Display video information with modern card design
        if st.session_state.current_video_loaded:
            st.divider()
            st.header("📊 Video Info")
            
            video_info = st.session_state.enhanced_chat_handler.get_video_info()
            
            if video_info:
                # Create a styled card for video info
                st.markdown('<div class="video-info-card">', unsafe_allow_html=True)
                
                # Display thumbnail if available
                if video_info.get('thumbnail'):
                    st.image(video_info['thumbnail'], use_container_width=True)
                
                # Display video details with better formatting
                if video_info.get('title'):
                    st.markdown(f"**🎬 Title**")
                    st.markdown(f"<p style='color: #AAAAAA; margin-top: -10px;'>{video_info['title']}</p>", unsafe_allow_html=True)
                
                if video_info.get('channel'):
                    st.markdown(f"**👤 Channel**")
                    st.markdown(f"<p style='color: #AAAAAA; margin-top: -10px;'>{video_info['channel']}</p>", unsafe_allow_html=True)
                
                if video_info.get('duration'):
                    st.markdown(f"**⏱️ Duration**")
                    st.markdown(f"<p style='color: #AAAAAA; margin-top: -10px;'>{video_info['duration']}</p>", unsafe_allow_html=True)
                
                # Display database status
                st.markdown(f"**💾 Database**")
                st.markdown(f"<p style='color: #00FF00; margin-top: -10px;'>✓ Stored with vector embeddings</p>", unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Feature buttons
                st.divider()
                st.header("🚀 Features")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📋 Summary", use_container_width=True):
                        with st.spinner("Generating summary..."):
                            summary = st.session_state.enhanced_chat_handler.get_video_summary()
                            st.session_state.video_summary = summary
                    
                    if st.button("🎬 Highlights", use_container_width=True):
                        with st.spinner("Extracting highlights..."):
                            highlights = st.session_state.enhanced_chat_handler.get_highlight_reel()
                            st.session_state.video_highlights = highlights
                
                with col2:
                    if st.button("😊 Mood Analysis", use_container_width=True):
                        with st.spinner("Analyzing mood..."):
                            mood = st.session_state.enhanced_chat_handler.get_video_mood_analysis()
                            st.session_state.video_mood = mood
                    
                    if st.button("📚 Video History", use_container_width=True):
                        st.session_state.show_history = True
                
                # Study Guide Features
                st.markdown("#### 📚 Study Tools")
                col3, col4, col5 = st.columns(3)
                
                with col3:
                    if st.button("📖 Study Guide", use_container_width=True):
                        with st.spinner("Generating comprehensive study guide..."):
                            study_guide = st.session_state.enhanced_chat_handler.generate_study_guide()
                            st.session_state.study_guide = study_guide
                            st.rerun()
                
                with col4:
                    if st.button("📝 Quick Notes", use_container_width=True):
                        with st.spinner("Generating study notes..."):
                            study_notes = st.session_state.enhanced_chat_handler.generate_study_notes()
                            st.session_state.study_notes = study_notes
                            st.rerun()
                
                with col5:
                    if st.button("🎯 Flashcards", use_container_width=True):
                        with st.spinner("Creating flashcards..."):
                            flashcards = st.session_state.enhanced_chat_handler.generate_flashcards(15)
                            st.session_state.flashcards = flashcards
                            st.rerun()
                
                # Display history if requested
                if st.session_state.get('show_history', False):
                    st.divider()
                    st.header("📚 Available Videos")
                    available_videos = st.session_state.enhanced_chat_handler.get_available_videos()
                    
                    if available_videos:
                        for video in available_videos:
                            with st.container():
                                st.markdown(f"**{video['title'][:50]}...**" if len(video['title']) > 50 else f"**{video['title']}**")
                                st.markdown(f"*{video['channel']} • {video['created_at']}*")
                                
                                if st.button(f"Load {video['video_id']}", key=f"load_{video['video_id']}", use_container_width=True):
                                    with st.spinner("Loading video..."):
                                        success = st.session_state.enhanced_chat_handler.load_video(video['video_id'])
                                        if success:
                                            st.session_state.current_video_loaded = True
                                            st.session_state.chat_history = []
                                            st.session_state.show_history = False
                                            st.rerun()
                                st.markdown("---")
                    else:
                        st.info("No videos in database yet. Load a video first!")
                    
                    if st.button("Hide History", use_container_width=True):
                        st.session_state.show_history = False
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.current_video_loaded:
            st.header("💬 Chat about the Video")
            
            # Display chat history
            chat_container = st.container()
            
            with chat_container:
                for message in st.session_state.chat_history:
                    if message["role"] == "user":
                        with st.chat_message("user"):
                            st.write(message["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(message["content"])
            
            # Chat input
            user_question = st.chat_input("Ask a question about the video...")
            
            if user_question:
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                
                # Get AI response using enhanced handler with vector search
                with st.spinner("Searching transcript and generating response..."):
                    try:
                        response = st.session_state.enhanced_chat_handler.get_response(
                            user_question, 
                            st.session_state.chat_history[:-1]  # Exclude the current question
                        )
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error getting response: {str(e)}")
        
        else:
            # Welcome message when no video is loaded with modern card design
            st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
            st.markdown("## 🚀 Welcome to YouTube Transcript Chat AI")
            st.markdown("""
            <div style='color: #AAAAAA; line-height: 1.6;'>
            Transform your YouTube watching experience with AI-powered conversations about video content.
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### How to Get Started")
            
            # Step-by-step guide with better styling
            st.markdown("""
            <div style='margin: 1.5rem 0;'>
                <div style='display: flex; align-items: center; margin: 1rem 0; padding: 1rem; background-color: #1a1a1a; border-radius: 8px; border-left: 4px solid #FF0000;'>
                    <div style='font-size: 1.5rem; margin-right: 1rem;'>1️⃣</div>
                    <div>
                        <strong style='color: #FFFFFF;'>Enter a YouTube Video ID</strong><br>
                        <span style='color: #AAAAAA;'>Enter the 11-character video ID (e.g., dQw4w9WgXcQ)</span>
                    </div>
                </div>
                
                <div style='display: flex; align-items: center; margin: 1rem 0; padding: 1rem; background-color: #1a1a1a; border-radius: 8px; border-left: 4px solid #065FD4;'>
                    <div style='font-size: 1.5rem; margin-right: 1rem;'>2️⃣</div>
                    <div>
                        <strong style='color: #FFFFFF;'>Load the Video</strong><br>
                        <span style='color: #AAAAAA;'>Click "Load Video" to extract the transcript automatically</span>
                    </div>
                </div>
                
                <div style='display: flex; align-items: center; margin: 1rem 0; padding: 1rem; background-color: #1a1a1a; border-radius: 8px; border-left: 4px solid #00FF00;'>
                    <div style='font-size: 1.5rem; margin-right: 1rem;'>3️⃣</div>
                    <div>
                        <strong style='color: #FFFFFF;'>Start Chatting</strong><br>
                        <span style='color: #AAAAAA;'>Ask questions about the video content using natural language</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### ✨ Key Features")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("""
                <div style='background-color: #1a1a1a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                    <strong style='color: #FF0000;'>🎯 Smart Context</strong><br>
                    <span style='color: #AAAAAA; font-size: 0.9rem;'>AI understands the full video content and context with citations</span>
                </div>
                
                <div style='background-color: #1a1a1a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                    <strong style='color: #065FD4;'>📊 Response Quality</strong><br>
                    <span style='color: #AAAAAA; font-size: 0.9rem;'>Faithfulness and quality metrics for every response</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown("""
                <div style='background-color: #1a1a1a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                    <strong style='color: #FF0000;'>🎬 Highlight Reel</strong><br>
                    <span style='color: #AAAAAA; font-size: 0.9rem;'>Extract key moments and important insights</span>
                </div>
                
                <div style='background-color: #1a1a1a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                    <strong style='color: #065FD4;'>😊 Mood Analysis</strong><br>
                    <span style='color: #AAAAAA; font-size: 0.9rem;'>Analyze video tone and emotional characteristics</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Feature panels
    with col2:
        if st.session_state.current_video_loaded:
            # Feature display panels
            if st.session_state.get('video_summary'):
                with st.expander("📋 Video Summary", expanded=False):
                    st.markdown(st.session_state.video_summary)
            
            if st.session_state.get('video_highlights'):
                with st.expander("🎬 Highlight Reel", expanded=False):
                    st.markdown(st.session_state.video_highlights)
            
            if st.session_state.get('video_mood'):
                with st.expander("😊 Mood Analysis", expanded=False):
                    st.markdown(st.session_state.video_mood)
            
            # Study Guide Features
            if st.session_state.get('study_guide'):
                with st.expander("📚 Study Guide", expanded=False):
                    guide = st.session_state.study_guide
                    if guide.get('error'):
                        st.error(guide['error'])
                    else:
                        st.markdown(f"**Overview:** {guide.get('overview', 'N/A')}")
                        
                        if guide.get('learning_objectives'):
                            st.markdown("**Learning Objectives:**")
                            for obj in guide['learning_objectives']:
                                st.markdown(f"• {obj}")
                        
                        if guide.get('key_concepts'):
                            st.markdown("**Key Concepts:**")
                            for concept in guide['key_concepts']:
                                if isinstance(concept, dict):
                                    st.markdown(f"• **{concept.get('term', 'Unknown')}**: {concept.get('definition', 'No definition')}")
                                else:
                                    st.markdown(f"• {concept}")
            
            if st.session_state.get('flashcards'):
                with st.expander("🎯 Flashcards", expanded=False):
                    cards = st.session_state.flashcards
                    if cards and len(cards) > 0 and not cards[0].get('error'):
                        for i, card in enumerate(cards[:10]):  # Show first 10 cards
                            with st.container():
                                st.markdown(f"**Card {i+1}** ({card.get('difficulty', 'medium')})")
                                st.markdown(f"**Q:** {card.get('question', 'No question')}")
                                with st.expander("Show Answer"):
                                    st.markdown(f"**A:** {card.get('answer', 'No answer')}")
                    else:
                        st.error("Failed to generate flashcards")
            
            if st.session_state.get('study_notes'):
                with st.expander("📝 Quick Study Notes", expanded=False):
                    notes = st.session_state.study_notes
                    if notes.get('error'):
                        st.error(notes['error'])
                    else:
                        st.markdown(f"**Summary:** {notes.get('summary', 'N/A')}")
                        
                        if notes.get('key_points'):
                            st.markdown("**Key Points:**")
                            for point in notes['key_points']:
                                st.markdown(f"• {point}")
                        
                        if notes.get('actionable_items'):
                            st.markdown("**Action Items:**")
                            for item in notes['actionable_items']:
                                st.markdown(f"✓ {item}")
            
            # Chat history counter
            if st.session_state.chat_history:
                st.markdown('<div class="chat-counter">', unsafe_allow_html=True)
                st.markdown(f"💬 **{len(st.session_state.chat_history)//2}** exchanges")
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
