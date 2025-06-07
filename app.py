import streamlit as st
import re
from youtube_utils import YouTubeTranscriptExtractor
from chat_handler import ChatHandler

# Page configuration
st.set_page_config(
    page_title="YouTube Transcript Chat AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'video_info' not in st.session_state:
    st.session_state.video_info = None
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'chat_handler' not in st.session_state:
    st.session_state.chat_handler = None

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
    st.title("🎬 YouTube Transcript Chat AI")
    st.markdown("Chat with YouTube videos using AI! Enter a video URL or ID to get started.")
    
    # Sidebar for video input and info
    with st.sidebar:
        st.header("📹 Video Input")
        
        # Video URL/ID input
        video_input = st.text_input(
            "YouTube URL or Video ID",
            placeholder="https://youtube.com/watch?v=... or video_id",
            help="Enter a YouTube video URL or just the video ID"
        )
        
        if st.button("Load Video", type="primary"):
            if video_input:
                video_id = extract_video_id(video_input)
                
                if video_id:
                    with st.spinner("Extracting transcript..."):
                        extractor = YouTubeTranscriptExtractor()
                        
                        try:
                            # Get video info and transcript
                            video_info = extractor.get_video_info(video_id)
                            transcript = extractor.get_transcript(video_id)
                            
                            if transcript:
                                st.session_state.video_info = video_info
                                st.session_state.transcript = transcript
                                st.session_state.chat_handler = ChatHandler(transcript, video_info)
                                st.session_state.chat_history = []  # Reset chat history
                                st.success("✅ Video loaded successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Could not extract transcript from this video.")
                                
                        except Exception as e:
                            st.error(f"❌ Error loading video: {str(e)}")
                else:
                    st.error("❌ Invalid YouTube URL or video ID")
            else:
                st.warning("⚠️ Please enter a YouTube URL or video ID")
        
        # Display video information
        if st.session_state.video_info:
            st.divider()
            st.header("📊 Video Info")
            
            video_info = st.session_state.video_info
            
            # Display thumbnail if available
            if video_info.get('thumbnail'):
                st.image(video_info['thumbnail'], use_column_width=True)
            
            # Display video details
            if video_info.get('title'):
                st.markdown(f"**Title:** {video_info['title']}")
            
            if video_info.get('duration'):
                st.markdown(f"**Duration:** {video_info['duration']}")
            
            if video_info.get('channel'):
                st.markdown(f"**Channel:** {video_info['channel']}")
            
            # Display transcript length
            if st.session_state.transcript:
                word_count = len(st.session_state.transcript.split())
                st.markdown(f"**Transcript:** {word_count} words")
    
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
            # Welcome message when no video is loaded
            st.header("🚀 Get Started")
            st.markdown("""
            Welcome to YouTube Transcript Chat AI! Here's how to use this app:
            
            1. **Enter a YouTube URL or Video ID** in the sidebar
            2. **Click "Load Video"** to extract the transcript
            3. **Start chatting** about the video content using AI
            
            ### Features:
            - 🎯 **Smart Context**: AI understands the video content
            - 💬 **Natural Chat**: Ask questions in plain English  
            - 📊 **Video Info**: See video details and thumbnail
            - 🔄 **Chat History**: Keep track of your conversation
            
            ### Example Questions:
            - "What are the main points discussed in this video?"
            - "Can you summarize the key takeaways?"
            - "What does the speaker say about [specific topic]?"
            - "At what time is [specific topic] mentioned?"
            """)
    
    with col2:
        if st.session_state.chat_history:
            st.header("🔧 Chat Controls")
            
            if st.button("Clear Chat History", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()
            
            st.markdown(f"**Messages:** {len(st.session_state.chat_history)}")
            
            # Export chat option
            if st.button("📥 Export Chat"):
                chat_text = ""
                for msg in st.session_state.chat_history:
                    role = "You" if msg["role"] == "user" else "AI"
                    chat_text += f"{role}: {msg['content']}\n\n"
                
                st.download_button(
                    label="Download Chat History",
                    data=chat_text,
                    file_name="youtube_chat_history.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
