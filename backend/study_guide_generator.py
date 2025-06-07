"""
AI-powered Study Guide Generator for YouTube videos
"""
import json
import os
from openai import OpenAI
from typing import Dict, List, Any

class StudyGuideGenerator:
    """Generates comprehensive study guides from video transcripts"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def generate_comprehensive_study_guide(self, video_id: str, transcript_text: str, video_info: dict) -> Dict[str, Any]:
        """
        Generate a comprehensive study guide with multiple sections
        """
        title = video_info.get('title', 'Unknown Video')
        channel = video_info.get('channel', 'Unknown Channel')
        
        study_guide_prompt = f"""
        Create a comprehensive study guide for this YouTube video transcript. The video is titled "{title}" by {channel}.
        
        Generate a structured study guide in JSON format with the following sections:
        
        1. "overview": A brief 2-3 sentence summary of the video's main topic
        2. "learning_objectives": 3-5 specific learning objectives students should achieve
        3. "key_concepts": List of 5-8 main concepts with brief definitions
        4. "detailed_outline": Hierarchical outline with main topics and subtopics
        5. "discussion_questions": 5-7 thought-provoking questions for deeper understanding
        6. "practice_exercises": 3-5 hands-on exercises or activities
        7. "additional_resources": Suggested topics for further research
        8. "quiz_questions": 10 multiple choice questions with answers
        9. "vocabulary": Important terms and definitions
        10. "takeaways": 3-5 key takeaways or action items
        
        Transcript:
        {transcript_text[:8000]}
        
        Respond only with valid JSON in the specified format.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": study_guide_prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            study_guide = json.loads(response.choices[0].message.content)
            return study_guide
            
        except Exception as e:
            return {
                "error": f"Failed to generate study guide: {str(e)}",
                "overview": "Study guide generation temporarily unavailable",
                "learning_objectives": [],
                "key_concepts": [],
                "detailed_outline": {},
                "discussion_questions": [],
                "practice_exercises": [],
                "additional_resources": [],
                "quiz_questions": [],
                "vocabulary": [],
                "takeaways": []
            }
    
    def generate_quick_study_notes(self, video_id: str, transcript_text: str, video_info: dict) -> Dict[str, Any]:
        """
        Generate quick study notes for rapid review
        """
        title = video_info.get('title', 'Unknown Video')
        
        notes_prompt = f"""
        Create quick study notes for this video: "{title}"
        
        Generate concise study notes in JSON format with:
        
        1. "summary": 1-2 sentence summary
        2. "key_points": 5-7 bullet points of main ideas
        3. "important_quotes": 3-5 significant quotes or statements
        4. "actionable_items": 3-5 concrete actions or next steps
        5. "time_stamps": Approximate time stamps for key sections (if identifiable)
        
        Transcript:
        {transcript_text[:6000]}
        
        Respond only with valid JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": notes_prompt}],
                response_format={"type": "json_object"},
                temperature=0.5
            )
            
            notes = json.loads(response.choices[0].message.content)
            return notes
            
        except Exception as e:
            return {
                "error": f"Failed to generate study notes: {str(e)}",
                "summary": "Study notes generation temporarily unavailable",
                "key_points": [],
                "important_quotes": [],
                "actionable_items": [],
                "time_stamps": []
            }
    
    def generate_flashcards(self, video_id: str, transcript_text: str, video_info: dict, num_cards: int = 15) -> List[Dict[str, str]]:
        """
        Generate flashcards for spaced repetition learning
        """
        title = video_info.get('title', 'Unknown Video')
        
        flashcards_prompt = f"""
        Create {num_cards} flashcards for studying this video: "{title}"
        
        Generate flashcards in JSON format as an array of objects, each with:
        - "question": The question or prompt (front of card)
        - "answer": The detailed answer (back of card)
        - "difficulty": "easy", "medium", or "hard"
        - "category": The topic category this card belongs to
        
        Mix different types of questions:
        - Factual recall
        - Conceptual understanding
        - Application scenarios
        - Analysis questions
        
        Transcript:
        {transcript_text[:7000]}
        
        Respond only with valid JSON array.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": flashcards_prompt}],
                response_format={"type": "json_object"},
                temperature=0.6
            )
            
            result = json.loads(response.choices[0].message.content)
            flashcards = result.get('flashcards', [])
            return flashcards
            
        except Exception as e:
            return [
                {
                    "question": "Flashcard generation error",
                    "answer": f"Failed to generate flashcards: {str(e)}",
                    "difficulty": "easy",
                    "category": "Error"
                }
            ]
    
    def generate_mind_map_data(self, video_id: str, transcript_text: str, video_info: dict) -> Dict[str, Any]:
        """
        Generate structured data for creating a mind map visualization
        """
        title = video_info.get('title', 'Unknown Video')
        
        mindmap_prompt = f"""
        Create mind map data for this video: "{title}"
        
        Generate a hierarchical structure in JSON format with:
        
        {
            "central_topic": "Main topic of the video",
            "main_branches": [
                {
                    "name": "Branch name",
                    "subtopics": ["subtopic1", "subtopic2", "subtopic3"],
                    "color": "color_code",
                    "importance": "high/medium/low"
                }
            ],
            "connections": [
                {
                    "from": "topic1",
                    "to": "topic2",
                    "relationship": "relationship_type"
                }
            ]
        }
        
        Create 4-6 main branches with 2-4 subtopics each.
        
        Transcript:
        {transcript_text[:6000]}
        
        Respond only with valid JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": mindmap_prompt}],
                response_format={"type": "json_object"},
                temperature=0.6
            )
            
            mindmap_data = json.loads(response.choices[0].message.content)
            return mindmap_data
            
        except Exception as e:
            return {
                "error": f"Failed to generate mind map: {str(e)}",
                "central_topic": "Mind map generation unavailable",
                "main_branches": [],
                "connections": []
            }
    
    def generate_learning_path(self, video_id: str, transcript_text: str, video_info: dict) -> Dict[str, Any]:
        """
        Generate a structured learning path based on video content
        """
        title = video_info.get('title', 'Unknown Video')
        
        learning_path_prompt = f"""
        Create a learning path for mastering the concepts in this video: "{title}"
        
        Generate a structured learning path in JSON format with:
        
        {
            "path_title": "Learning path title",
            "estimated_time": "Total estimated learning time",
            "difficulty_level": "beginner/intermediate/advanced",
            "prerequisites": ["prerequisite1", "prerequisite2"],
            "learning_modules": [
                {
                    "module_number": 1,
                    "title": "Module title",
                    "description": "What students will learn",
                    "estimated_time": "Time estimate",
                    "activities": ["activity1", "activity2"],
                    "assessment": "How progress is measured"
                }
            ],
            "final_project": "Capstone project or final assessment",
            "next_steps": ["suggestions for continued learning"]
        }
        
        Create 3-5 progressive learning modules.
        
        Transcript:
        {transcript_text[:6000]}
        
        Respond only with valid JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": learning_path_prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            learning_path = json.loads(response.choices[0].message.content)
            return learning_path
            
        except Exception as e:
            return {
                "error": f"Failed to generate learning path: {str(e)}",
                "path_title": "Learning path generation unavailable",
                "estimated_time": "Unknown",
                "difficulty_level": "unknown",
                "prerequisites": [],
                "learning_modules": [],
                "final_project": "Unavailable",
                "next_steps": []
            }