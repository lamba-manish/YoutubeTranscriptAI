import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import streamlit as st

class YouTubeTranscriptExtractor:
    """Utility class for extracting YouTube video transcripts and metadata"""
    
    def __init__(self):
        self.formatter = TextFormatter()
    
    def get_video_info(self, video_id):
        """
        Extract video information using YouTube oEmbed API
        Returns dict with title, thumbnail, duration, and channel info
        """
        try:
            # Use YouTube oEmbed API to get video info
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = requests.get(oembed_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'title': data.get('title', 'Unknown Title'),
                    'channel': data.get('author_name', 'Unknown Channel'),
                    'thumbnail': data.get('thumbnail_url', ''),
                    'duration': self._format_duration(data.get('duration', 0)),
                    'video_id': video_id
                }
            else:
                # Fallback with basic info
                return {
                    'title': f'Video ID: {video_id}',
                    'channel': 'Unknown Channel',
                    'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                    'duration': 'Unknown',
                    'video_id': video_id
                }
                
        except Exception as e:
            st.warning(f"Could not fetch video metadata: {str(e)}")
            # Return basic fallback info
            return {
                'title': f'Video ID: {video_id}',
                'channel': 'Unknown Channel', 
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
                'duration': 'Unknown',
                'video_id': video_id
            }
    
    def get_transcript(self, video_id, languages=['en', 'en-US', 'en-GB']):
        """
        Extract transcript from YouTube video
        Returns formatted transcript text or None if not available
        """
        try:
            # Try to get transcript in preferred languages
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # First try to find manual transcripts in preferred languages
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    if not transcript.is_generated:
                        return self._format_transcript(transcript.fetch())
                except:
                    continue
            
            # If no manual transcript found, try auto-generated in preferred languages
            for lang in languages:
                try:
                    transcript = transcript_list.find_generated_transcript([lang])
                    return self._format_transcript(transcript.fetch())
                except:
                    continue
            
            # If still no transcript found, try any available transcript
            try:
                transcript = transcript_list.find_transcript(['en'])
                return self._format_transcript(transcript.fetch())
            except:
                pass
            
            # Last resort: try any available transcript
            try:
                available_transcripts = transcript_list._manually_created_transcripts
                if not available_transcripts:
                    available_transcripts = transcript_list._generated_transcripts
                
                if available_transcripts:
                    first_transcript = list(available_transcripts.values())[0]
                    return self._format_transcript(first_transcript.fetch())
            except:
                pass
            
            return None
            
        except Exception as e:
            st.error(f"Error extracting transcript: {str(e)}")
            return None
    
    def _format_transcript(self, transcript_data):
        """
        Format transcript data into readable text with timestamps
        """
        try:
            # Create formatted text with timestamps
            formatted_text = ""
            
            for entry in transcript_data:
                start_time = self._seconds_to_timestamp(entry['start'])
                text = entry['text'].strip()
                
                # Clean up the text
                text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                text = text.replace('\n', ' ')    # Remove line breaks
                
                if text:  # Only add non-empty text
                    formatted_text += f"[{start_time}] {text}\n"
            
            return formatted_text.strip()
            
        except Exception as e:
            st.error(f"Error formatting transcript: {str(e)}")
            return None
    
    def _seconds_to_timestamp(self, seconds):
        """Convert seconds to MM:SS or HH:MM:SS format"""
        try:
            seconds = int(float(seconds))
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        except:
            return "00:00"
    
    def _format_duration(self, duration_seconds):
        """Format duration from seconds to readable format"""
        try:
            if isinstance(duration_seconds, (int, float)) and duration_seconds > 0:
                return self._seconds_to_timestamp(duration_seconds)
            return "Unknown"
        except:
            return "Unknown"
    
    def search_transcript(self, transcript, query, context_words=50):
        """
        Search for specific terms in transcript and return relevant sections
        """
        if not transcript or not query:
            return []
        
        # Split transcript into lines
        lines = transcript.split('\n')
        results = []
        
        query_lower = query.lower()
        
        for i, line in enumerate(lines):
            if query_lower in line.lower():
                # Extract timestamp if present
                timestamp_match = re.match(r'^\[([^\]]+)\]', line)
                timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"
                
                # Get context around the match
                start_idx = max(0, i - 2)
                end_idx = min(len(lines), i + 3)
                context = ' '.join([re.sub(r'^\[[^\]]+\]\s*', '', l) for l in lines[start_idx:end_idx]])
                
                results.append({
                    'timestamp': timestamp,
                    'context': context,
                    'line': line
                })
        
        return results
