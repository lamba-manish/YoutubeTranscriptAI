import streamlit as st
import re
import os
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
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.video_info and st.session_state.chat_handler:
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
                
                # Get AI response
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.chat_handler.get_response(
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
                    <span style='color: #AAAAAA; font-size: 0.9rem;'>AI understands the full video content and context</span>
                </div>
                
                <div style='background-color: #1a1a1a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                    <strong style='color: #065FD4;'>📊 Video Analytics</strong><br>
                    <span style='color: #AAAAAA; font-size: 0.9rem;'>View video details, thumbnails, and transcript stats</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown("""
                <div style='background-color: #1a1a1a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                    <strong style='color: #00FF00;'>💬 Natural Chat</strong><br>
                    <span style='color: #AAAAAA; font-size: 0.9rem;'>Ask questions in plain English, get detailed answers</span>
                </div>
                
                <div style='background-color: #1a1a1a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                    <strong style='color: #FFC107;'>🔄 Chat Memory</strong><br>
                    <span style='color: #AAAAAA; font-size: 0.9rem;'>Maintains conversation history and context</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 🎯 Try These Video IDs")
            
            example_videos = [
                {"id": "Gfr50f6ZBvo", "title": "Podcast Interview", "note": "Long-form conversation"},
                {"id": "dQw4w9WgXcQ", "title": "Rick Astley - Never Gonna Give You Up", "note": "Classic music video"},
                {"id": "9bZkp7q19f0", "title": "TED Talk example", "note": "Educational content"}
            ]
            
            for video in example_videos:
                st.markdown(f"""
                <div style='background-color: #1a1a1a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #FF0000;'>
                    <div style='color: #FFFFFF; font-weight: bold; margin-bottom: 0.3rem;'>{video['title']}</div>
                    <div style='color: #065FD4; font-family: monospace; font-size: 1.1rem; margin-bottom: 0.3rem;'>{video['id']}</div>
                    <div style='color: #AAAAAA; font-size: 0.9rem;'>{video['note']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 💡 Example Questions to Try")
            
            example_questions = [
                "What are the main points discussed in this video?",
                "Can you summarize the key takeaways?",
                "What does the speaker say about [specific topic]?",
                "At what time is [specific topic] mentioned?",
                "What are the most important quotes from this video?",
                "Can you explain [complex concept] mentioned in the video?"
            ]
            
            for i, question in enumerate(example_questions):
                st.markdown(f"""
                <div style='background-color: #1a1a1a; padding: 0.8rem; border-radius: 6px; margin: 0.3rem 0; border-left: 2px solid #AAAAAA;'>
                    <span style='color: #AAAAAA; font-style: italic;'>"{question}"</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.chat_history:
            st.markdown('<div class="video-info-card">', unsafe_allow_html=True)
            st.header("🔧 Chat Controls")
            
            # Chat statistics
            message_count = len(st.session_state.chat_history)
            user_messages = len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])
            ai_messages = len([msg for msg in st.session_state.chat_history if msg["role"] == "assistant"])
            
            st.markdown(f"""
            <div style='background-color: #1a1a1a; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                <div style='text-align: center;'>
                    <div style='color: #FF0000; font-size: 1.5rem; font-weight: bold;'>{message_count}</div>
                    <div style='color: #AAAAAA; font-size: 0.9rem;'>Total Messages</div>
                </div>
                <hr style='margin: 0.5rem 0; border-color: #303030;'>
                <div style='display: flex; justify-content: space-between;'>
                    <div style='text-align: center;'>
                        <div style='color: #065FD4; font-weight: bold;'>{user_messages}</div>
                        <div style='color: #AAAAAA; font-size: 0.8rem;'>You</div>
                    </div>
                    <div style='text-align: center;'>
                        <div style='color: #00FF00; font-weight: bold;'>{ai_messages}</div>
                        <div style='color: #AAAAAA; font-size: 0.8rem;'>AI</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Control buttons
            st.markdown("### Actions")
            
            if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
            
            # Export chat option
            if st.button("📥 Export Chat", type="secondary", use_container_width=True):
                chat_text = f"YouTube Transcript Chat - Export\n"
                chat_text += f"Video: {st.session_state.video_info.get('title', 'Unknown')}\n"
                chat_text += f"Channel: {st.session_state.video_info.get('channel', 'Unknown')}\n"
                chat_text += f"Export Date: {st.session_state.chat_history[-1].get('timestamp', 'Unknown') if st.session_state.chat_history else 'Unknown'}\n"
                chat_text += "=" * 50 + "\n\n"
                
                for i, msg in enumerate(st.session_state.chat_history):
                    role = "You" if msg["role"] == "user" else "AI Assistant"
                    chat_text += f"[{i+1}] {role}:\n{msg['content']}\n\n"
                
                st.download_button(
                    label="⬇️ Download Chat History",
                    data=chat_text,
                    file_name=f"youtube_chat_{st.session_state.video_info.get('video_id', 'unknown')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick actions section (always visible)
        elif st.session_state.video_info and st.session_state.chat_handler:
            st.markdown('<div class="video-info-card">', unsafe_allow_html=True)
            st.header("⚡ Quick Actions")
            
            st.markdown("Try these preset questions:")
            
            quick_questions = [
                "📋 Summarize this video",
                "🔑 What are the key points?",
                "💡 Give me the main takeaways",
                "🎯 What's the conclusion?"
            ]
            
            for question in quick_questions:
                if st.button(question, use_container_width=True):
                    # Extract the actual question text
                    question_text = question.split(" ", 1)[1]  # Remove emoji
                    
                    # Add to chat history
                    st.session_state.chat_history.append({"role": "user", "content": question_text})
                    
                    # Get AI response
                    with st.spinner("Thinking..."):
                        try:
                            response = st.session_state.chat_handler.get_response(
                                question_text, 
                                st.session_state.chat_history[:-1]
                            )
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
