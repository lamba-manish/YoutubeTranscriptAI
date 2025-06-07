import os
from openai import OpenAI
import streamlit as st

class ChatHandler:
    """Handles AI-powered conversations about YouTube video transcripts"""
    
    def __init__(self, transcript, video_info):
        self.transcript = transcript
        self.video_info = video_info
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            st.error("❌ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            st.stop()
        
        self.client = OpenAI(api_key=api_key)
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        
        # Create system prompt with video context
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self):
        """Create a comprehensive system prompt with video context"""
        
        video_title = self.video_info.get('title', 'Unknown Video')
        video_channel = self.video_info.get('channel', 'Unknown Channel')
        
        system_prompt = f"""You are an AI assistant specialized in discussing YouTube video content. 

VIDEO INFORMATION:
- Title: {video_title}
- Channel: {video_channel}
- Video ID: {self.video_info.get('video_id', 'Unknown')}

You have access to the complete transcript of this video. Use this transcript to answer questions accurately and provide specific information about what was discussed in the video.

TRANSCRIPT:
{self.transcript}

INSTRUCTIONS:
1. Answer questions based solely on the video transcript content
2. Provide specific quotes or references when possible
3. Include timestamps when mentioning specific parts of the video
4. If asked about something not covered in the transcript, clearly state that
5. Be conversational and helpful while staying accurate to the content
6. When discussing time-based content, reference the timestamps from the transcript
7. Summarize or explain complex topics from the video in an accessible way
8. If asked for specific quotes, provide them exactly as they appear in the transcript

Remember: Your knowledge is limited to what's in this video transcript. Don't add information from your general knowledge that wasn't mentioned in the video."""

        return system_prompt
    
    def get_response(self, user_question, chat_history=None):
        """
        Generate AI response based on the video transcript and chat history
        """
        try:
            # Prepare messages for the API call
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history[-10:]:  # Limit to last 10 messages for context
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current user question
            messages.append({
                "role": "user", 
                "content": user_question
            })
            
            # Make API call to OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Failed to get AI response: {str(e)}")
    
    def get_video_summary(self):
        """Generate a comprehensive summary of the video"""
        try:
            summary_prompt = """Please provide a comprehensive summary of this video including:
1. Main topics discussed
2. Key points and takeaways
3. Important quotes or statements
4. Overall theme and conclusion

Structure your response in a clear, organized way."""
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": summary_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1500,
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    def extract_key_quotes(self, topic=None):
        """Extract key quotes from the video, optionally filtered by topic"""
        try:
            if topic:
                quote_prompt = f"""Extract key quotes from the video related to "{topic}". 
Include the timestamp for each quote and provide context for why it's important."""
            else:
                quote_prompt = """Extract the most important and memorable quotes from this video. 
Include timestamps and brief context for each quote."""
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": quote_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Failed to extract quotes: {str(e)}")
    
    def find_timestamp_for_topic(self, topic):
        """Find when a specific topic is discussed in the video"""
        try:
            timestamp_prompt = f"""When in the video is "{topic}" discussed? 
Provide the specific timestamp(s) and a brief description of what is said about this topic."""
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": timestamp_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Failed to find timestamp: {str(e)}")
