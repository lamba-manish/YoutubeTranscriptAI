"""
Enhanced chat handler using LangChain and vector embeddings
"""
import os
from backend.database import DatabaseManager
from backend.vector_manager import VectorManager
from backend.evaluation_system import ResponseEvaluator
import streamlit as st

class EnhancedChatHandler:
    """Enhanced chat handler with database integration and vector search"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.vector_manager = VectorManager(self.db_manager)
        self.evaluator = ResponseEvaluator()
        self.current_video_id = None
        self.current_video_info = None
    
    def load_video(self, video_id: str, transcript_text: str = None, video_info: dict = None):
        """
        Load video transcript, either from database or by processing new transcript
        """
        try:
            # Check if video already exists in database
            if self.db_manager.video_exists(video_id):
                print(f"Debug - Video {video_id} found in database")
                st.success("✅ Video transcript found in database! Loading existing data...")
                
                # Load from database
                video_data = self.db_manager.get_video_transcript(video_id)
                self.current_video_id = video_id
                self.current_video_info = {
                    'video_id': video_data['video_id'],
                    'title': video_data['title'],
                    'channel': video_data['channel'],
                    'duration': video_data['duration'],
                    'thumbnail': video_data['thumbnail']
                }
                return True
            
            # If not in database, save new transcript
            elif transcript_text and video_info:
                print(f"Debug - Saving new video {video_id} to database")
                
                # Save transcript and metadata
                self.db_manager.save_video_transcript(video_id, transcript_text, video_info)
                
                # Process embeddings in background
                with st.spinner("Processing transcript for AI chat (this may take a moment)..."):
                    success = self.vector_manager.process_video_transcript(
                        video_id, transcript_text, video_info
                    )
                
                if success:
                    self.current_video_id = video_id
                    self.current_video_info = video_info
                    st.success("✅ Video transcript processed and saved to database!")
                    return True
                else:
                    st.error("❌ Error processing transcript embeddings")
                    return False
            
            else:
                st.error("❌ No transcript data provided and video not found in database")
                return False
                
        except Exception as e:
            print(f"Debug - Error loading video: {str(e)}")
            st.error(f"❌ Error loading video: {str(e)}")
            return False
    
    def get_response(self, user_question: str, chat_history: list = None) -> str:
        """
        Get AI response using vector similarity search
        """
        if not self.current_video_id:
            return "Please load a video first before asking questions."
        
        try:
            # Get AI response using vector search
            response, context = self.vector_manager.query_transcript_with_context(
                self.current_video_id, 
                user_question
            )
            
            # Evaluate response quality
            try:
                evaluation_scores = self.evaluator.evaluate_response(
                    user_question, response, context
                )
                evaluation_summary = self.evaluator.get_evaluation_summary(evaluation_scores)
                
                # Append evaluation scores to response
                enhanced_response = f"{response}\n\n---\n{evaluation_summary}"
                return enhanced_response
                
            except Exception as eval_error:
                print(f"Debug - Error evaluating response: {eval_error}")
                # Return response without evaluation if evaluation fails
                return response
            
        except Exception as e:
            print(f"Debug - Error getting response: {str(e)}")
            return f"Sorry, I encountered an error while processing your question: {str(e)}"
    
    def get_video_summary(self) -> str:
        """
        Generate video summary using vector embeddings
        """
        if not self.current_video_id:
            return "Please load a video first before requesting a summary."
        
        try:
            summary = self.vector_manager.get_video_summary(self.current_video_id)
            return summary
            
        except Exception as e:
            print(f"Debug - Error generating summary: {str(e)}")
            return f"Sorry, I encountered an error while generating the summary: {str(e)}"
    
    def get_video_info(self) -> dict:
        """
        Get current video information
        """
        return self.current_video_info
    
    def is_video_loaded(self) -> bool:
        """
        Check if a video is currently loaded
        """
        return self.current_video_id is not None
    
    def get_highlight_reel(self, num_highlights: int = 5) -> str:
        """
        Get highlight reel for current video
        """
        if not self.current_video_id:
            return "Please load a video first."
        
        return self.vector_manager.extract_highlight_reel(self.current_video_id, num_highlights)
    
    def get_video_mood_analysis(self) -> str:
        """
        Get mood and tone analysis for current video
        """
        if not self.current_video_id:
            return "Please load a video first."
        
        return self.vector_manager.analyze_video_mood(self.current_video_id)
    
    def get_available_videos(self) -> list:
        """
        Get list of all available videos in database
        """
        return self.db_manager.get_all_videos()