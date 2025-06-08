import re
import requests
import time
import json
from urllib.parse import unquote
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import streamlit as st

class YouTubeTranscriptExtractor:
    """Utility class for extracting YouTube video transcripts and metadata"""
    
    def __init__(self):
        pass
    
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
    
    def get_transcript(self, video_id, languages=['en']):
        """
        Extract transcript using direct HTTP approach for better reliability
        Returns formatted transcript text or None if not available
        """
        # First try the direct HTTP approach
        transcript = self._get_transcript_direct(video_id)
        if transcript:
            return transcript
            
        # Fallback to youtube-transcript-api with multi-language support
        try:
            print(f"Debug - Fallback: Using youtube-transcript-api for {video_id}")
            
            # Try to get available transcripts
            transcript_list_data = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # First try English
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                if transcript_list and len(transcript_list) > 0:
                    print(f"Debug - Found English transcript with {len(transcript_list)} segments")
                    return self._format_transcript(transcript_list)
            except:
                pass
            
            # If English not available, try other languages and translate
            for transcript in transcript_list_data:
                try:
                    if transcript.language_code != 'en' and transcript.is_translatable:
                        # Get transcript and translate to English
                        translated_transcript = transcript.translate('en').fetch()
                        if translated_transcript and len(translated_transcript) > 0:
                            print(f"Debug - Found {transcript.language} transcript, translated to English with {len(translated_transcript)} segments")
                            return self._format_transcript(translated_transcript)
                except Exception as translate_error:
                    print(f"Debug - Translation failed for {transcript.language_code}: {translate_error}")
                    continue
            
            # If translation fails, try original language
            for transcript in transcript_list_data:
                try:
                    original_transcript = transcript.fetch()
                    if original_transcript and len(original_transcript) > 0:
                        print(f"Debug - Using original {transcript.language} transcript with {len(original_transcript)} segments")
                        return self._format_transcript(original_transcript)
                except Exception as orig_error:
                    print(f"Debug - Original transcript failed for {transcript.language_code}: {orig_error}")
                    continue
                
        except TranscriptsDisabled:
            st.error("This video does not have captions available.")
            return None
        except Exception as e:
            print(f"Debug - Fallback failed: {str(e)}")
        
        st.error("Could not extract transcript from this video. The video may not have captions available.")
        return None
    
    def _get_transcript_direct(self, video_id):
        """
        Direct HTTP method to extract transcript from YouTube
        """
        try:
            print(f"Debug - Trying direct HTTP approach for {video_id}")
            
            # Get the video page
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(video_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Debug - HTTP error: {response.status_code}")
                return None
            
            content = response.text
            
            # Look for transcript data in the page
            # YouTube embeds transcript URLs in the page source
            transcript_pattern = r'"captionTracks":\s*\[([^\]]+)\]'
            match = re.search(transcript_pattern, content)
            
            if not match:
                print("Debug - No caption tracks found in page")
                return None
            
            caption_data = match.group(1)
            
            # Extract the base URL for English captions
            url_pattern = r'"baseUrl":"([^"]+)"[^}]*"languageCode":"en"'
            url_match = re.search(url_pattern, caption_data)
            
            if not url_match:
                print("Debug - No English caption URL found")
                return None
            
            caption_url = url_match.group(1).replace('\\u0026', '&')
            print(f"Debug - Found caption URL")
            
            # Fetch the actual transcript
            caption_response = requests.get(caption_url, headers=headers, timeout=10)
            if caption_response.status_code != 200:
                print(f"Debug - Caption fetch error: {caption_response.status_code}")
                return None
            
            return self._parse_xml_transcript(caption_response.text)
            
        except Exception as e:
            print(f"Debug - Direct method error: {str(e)}")
            return None
    
    def _parse_xml_transcript(self, xml_content):
        """
        Parse XML transcript content and format it
        """
        try:
            # Simple regex parsing of XML transcript
            text_pattern = r'<text start="([^"]+)"[^>]*>([^<]+)</text>'
            matches = re.findall(text_pattern, xml_content)
            
            if not matches:
                print("Debug - No text segments found in XML")
                return None
            
            formatted_text = ""
            for start_time, text in matches:
                try:
                    # Convert start time to readable format
                    start_seconds = float(start_time)
                    timestamp = self._seconds_to_timestamp(start_seconds)
                    
                    # Clean up the text
                    clean_text = unquote(text).replace('&quot;', '"').replace('&amp;', '&')
                    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                    
                    if clean_text:
                        formatted_text += f"[{timestamp}] {clean_text}\n"
                        
                except Exception as e:
                    print(f"Debug - Error parsing segment: {e}")
                    continue
            
            if formatted_text:
                print(f"Debug - Successfully parsed {len(matches)} transcript segments")
                return formatted_text.strip()
            
            return None
            
        except Exception as e:
            print(f"Debug - XML parsing error: {str(e)}")
            return None
    
    def _format_transcript(self, transcript_data):
        """
        Format transcript data into readable text with timestamps
        """
        try:
            # Create formatted text with timestamps
            formatted_text = ""
            
            for entry in transcript_data:
                try:
                    # Handle both dict and object attribute access patterns
                    if hasattr(entry, 'start') and hasattr(entry, 'text'):
                        # Object attribute access (FetchedTranscriptSnippet)
                        start = entry.start
                        text = entry.text
                    elif isinstance(entry, dict):
                        # Dictionary access
                        start = entry.get('start', 0)
                        text = entry.get('text', '')
                    else:
                        # Try both approaches as fallback
                        try:
                            start = entry['start']
                            text = entry['text']
                        except (KeyError, TypeError):
                            start = getattr(entry, 'start', 0)
                            text = getattr(entry, 'text', '')
                    
                    # Convert start time and clean text
                    start_time = self._seconds_to_timestamp(start)
                    text = str(text).strip()
                    
                    # Clean up the text
                    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                    text = text.replace('\n', ' ')    # Remove line breaks
                    
                    if text:  # Only add non-empty text
                        formatted_text += f"[{start_time}] {text}\n"
                        
                except Exception as entry_error:
                    print(f"Debug - Error processing transcript entry: {entry_error}")
                    continue
            
            return formatted_text.strip() if formatted_text else None
            
        except Exception as e:
            print(f"Error formatting transcript: {str(e)}")
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
