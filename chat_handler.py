import os
import re
from openai import OpenAI
import streamlit as st

class ChatHandler:
    """Handles AI-powered conversations about YouTube video transcripts"""
    
    def __init__(self, transcript, video_info):
        self.full_transcript = transcript  # Keep full transcript for searching
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
        
        # Calculate transcript length and chunk if necessary
        transcript_text = self.transcript
        max_transcript_length = 15000  # Conservative limit to avoid token issues
        
        if len(transcript_text) > max_transcript_length:
            print(f"Debug - Transcript too long ({len(transcript_text)} chars), chunking...")
            # Keep first part and last part of transcript for context
            chunk_size = max_transcript_length // 2
            transcript_text = (
                transcript_text[:chunk_size] + 
                "\n\n[... MIDDLE SECTION TRUNCATED FOR BREVITY ...]\n\n" + 
                transcript_text[-chunk_size:]
            )
            print(f"Debug - Chunked transcript to {len(transcript_text)} chars")
        
        system_prompt = f"""You are an AI assistant specialized in discussing YouTube video content. 

VIDEO INFORMATION:
- Title: {video_title}
- Channel: {video_channel}
- Video ID: {self.video_info.get('video_id', 'Unknown')}

You have access to the transcript of this video. Use this transcript to answer questions accurately and provide specific information about what was discussed in the video.

TRANSCRIPT:
{transcript_text}

INSTRUCTIONS:
1. Answer questions based on the video transcript content provided
2. Provide specific quotes or references when possible
3. Include timestamps when mentioning specific parts of the video
4. If asked about something not covered in the transcript excerpt, mention that you have access to a portion of the transcript
5. Be conversational and helpful while staying accurate to the content
6. When discussing time-based content, reference the timestamps from the transcript
7. Summarize or explain complex topics from the video in an accessible way
8. If asked for specific quotes, provide them exactly as they appear in the transcript

Remember: Your knowledge is based on this video transcript. Focus on the content that was actually discussed in the video."""

        return system_prompt
    
    def _find_relevant_transcript_sections(self, question, max_chars=8000):
        """
        Find relevant sections of transcript based on the question
        """
        question_lower = question.lower()
        lines = self.full_transcript.split('\n')
        relevant_lines = []
        
        # Keywords from the question
        keywords = re.findall(r'\b\w+\b', question_lower)
        keywords = [k for k in keywords if len(k) > 3]  # Filter short words
        
        # Score each line based on keyword matches
        scored_lines = []
        for i, line in enumerate(lines):
            score = 0
            line_lower = line.lower()
            
            for keyword in keywords:
                if keyword in line_lower:
                    score += line_lower.count(keyword)
            
            if score > 0:
                # Include some context around matching lines
                start = max(0, i-2)
                end = min(len(lines), i+3)
                context = '\n'.join(lines[start:end])
                scored_lines.append((score, context))
        
        # Sort by relevance and combine top sections
        scored_lines.sort(reverse=True, key=lambda x: x[0])
        
        combined_text = ""
        used_texts = set()
        
        for score, text in scored_lines[:10]:  # Top 10 relevant sections
            if text not in used_texts and len(combined_text + text) < max_chars:
                combined_text += text + "\n\n"
                used_texts.add(text)
        
        # If no relevant sections found, use beginning and end
        if not combined_text:
            chunk_size = max_chars // 2
            combined_text = (
                self.full_transcript[:chunk_size] + 
                "\n\n[... MIDDLE SECTION OMITTED ...]\n\n" + 
                self.full_transcript[-chunk_size:]
            )
        
        return combined_text.strip()

    def get_response(self, user_question, chat_history=None):
        """
        Generate AI response based on relevant transcript sections and chat history
        """
        try:
            # Find relevant transcript sections for this specific question
            relevant_transcript = self._find_relevant_transcript_sections(user_question)
            
            # Create a focused system prompt with relevant content
            video_title = self.video_info.get('title', 'Unknown Video')
            video_channel = self.video_info.get('channel', 'Unknown Channel')
            
            focused_prompt = f"""You are an AI assistant specialized in discussing YouTube video content.

VIDEO INFORMATION:
- Title: {video_title}
- Channel: {video_channel}
- Video ID: {self.video_info.get('video_id', 'Unknown')}

RELEVANT TRANSCRIPT SECTIONS:
{relevant_transcript}

INSTRUCTIONS:
1. Answer questions based on the transcript content provided
2. Provide specific quotes with timestamps when possible
3. If the answer requires information not in these sections, mention that you would need to see more of the transcript
4. Be conversational and helpful while staying accurate to the content
5. Reference timestamps from the transcript when discussing specific moments

Remember: Focus on what's actually discussed in the provided transcript sections."""
            
            # Prepare messages for the API call
            messages = [
                {"role": "system", "content": focused_prompt}
            ]
            
            # Add recent chat history if provided
            if chat_history:
                for msg in chat_history[-5:]:  # Limit to last 5 messages for context
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
