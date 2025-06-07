# API Documentation - YouTube Transcript Chat AI

## Table of Contents
1. [Core Classes](#core-classes)
2. [Database Models](#database-models)
3. [Error Handling](#error-handling)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)

## Core Classes

### EnhancedChatHandler

Main interface for video processing and AI interactions.

```python
class EnhancedChatHandler:
    """Enhanced chat handler with database integration and vector search"""
    
    def __init__(self) -> None:
        """Initialize handler with database, vector manager, and AI services"""
    
    def load_video(self, video_id: str, transcript_text: str = None, 
                   video_info: dict = None) -> bool:
        """
        Load video transcript, either from database or by processing new transcript
        
        Args:
            video_id: YouTube video ID (11 characters)
            transcript_text: Optional pre-extracted transcript
            video_info: Optional video metadata
            
        Returns:
            bool: Success status
        """
    
    def get_response(self, user_question: str, chat_history: list = None) -> str:
        """
        Get AI response using vector similarity search
        
        Args:
            user_question: User's question about the video
            chat_history: Previous conversation history
            
        Returns:
            str: AI-generated response with citations
        """
    
    def get_video_summary(self) -> str:
        """Generate comprehensive video summary"""
    
    def get_highlight_reel(self, num_highlights: int = 5) -> str:
        """Extract key moments from video"""
    
    def get_video_mood_analysis(self) -> str:
        """Analyze video tone and emotional characteristics"""
    
    def generate_study_guide(self) -> dict:
        """Generate comprehensive study guide with learning objectives"""
    
    def generate_flashcards(self, num_cards: int = 15) -> list:
        """Create interactive flashcards for spaced repetition"""
    
    def generate_study_notes(self) -> dict:
        """Generate quick study notes with actionable insights"""
```

### StudyGuideGenerator

AI-powered educational content generator.

```python
class StudyGuideGenerator:
    """Generates comprehensive study guides from video transcripts"""
    
    def generate_comprehensive_study_guide(self, video_id: str, 
                                         transcript_text: str, 
                                         video_info: dict) -> Dict[str, Any]:
        """
        Generate complete study guide with multiple sections
        
        Returns:
            dict: {
                'overview': str,
                'learning_objectives': List[str],
                'key_concepts': List[dict],
                'detailed_outline': dict,
                'discussion_questions': List[str],
                'practice_exercises': List[str],
                'quiz_questions': List[dict],
                'vocabulary': List[dict],
                'takeaways': List[str]
            }
        """
    
    def generate_flashcards(self, video_id: str, transcript_text: str, 
                           video_info: dict, num_cards: int = 15) -> List[Dict[str, str]]:
        """
        Generate flashcards for spaced repetition learning
        
        Returns:
            list: [
                {
                    'question': str,
                    'answer': str,
                    'difficulty': 'easy'|'medium'|'hard',
                    'category': str
                }
            ]
        """
    
    def generate_quick_study_notes(self, video_id: str, transcript_text: str, 
                                  video_info: dict) -> Dict[str, Any]:
        """
        Generate concise study notes for rapid review
        
        Returns:
            dict: {
                'summary': str,
                'key_points': List[str],
                'important_quotes': List[str],
                'actionable_items': List[str],
                'time_stamps': List[dict]
            }
        """
```

### VectorManager

Handles embedding generation and similarity search using FAISS.

```python
class VectorManager:
    """Manages vector embeddings and similarity search using LangChain"""
    
    def process_video_transcript(self, video_id: str, transcript_text: str, 
                                video_info: dict) -> bool:
        """
        Process and store video transcript with embeddings
        
        Args:
            video_id: Unique video identifier
            transcript_text: Full transcript content
            video_info: Video metadata
            
        Returns:
            bool: Processing success status
        """
    
    def query_transcript_with_context(self, video_id: str, question: str, 
                                    k: int = 4) -> tuple[str, str]:
        """
        Query transcript using vector similarity search
        
        Args:
            video_id: Video to search
            question: User's question
            k: Number of similar chunks to retrieve
            
        Returns:
            tuple: (ai_response, source_context)
        """
    
    def create_vector_store(self, video_id: str) -> FAISS:
        """Create FAISS vector store from stored embeddings"""
```

### ResponseEvaluator

Evaluates AI responses for quality and faithfulness.

```python
class ResponseEvaluator:
    """Evaluates AI responses for faithfulness, relevance, and quality"""
    
    def evaluate_response(self, question: str, response: str, 
                         context: str) -> Dict[str, float]:
        """
        Evaluate AI response with multiple metrics
        
        Args:
            question: User's original question
            response: AI's generated response
            context: Source context from transcript
            
        Returns:
            dict: {
                'faithfulness': float,  # 0.0 to 1.0
                'relevance': float,     # 0.0 to 1.0
                'completeness': float,  # 0.0 to 1.0
                'clarity': float,       # 0.0 to 1.0
                'overall_score': float  # 0.0 to 1.0
            }
        """
```

## Usage Examples

### Basic Video Processing

```python
from backend.enhanced_chat_handler import EnhancedChatHandler

def process_video():
    handler = EnhancedChatHandler()
    
    # Load video
    success = handler.load_video("dQw4w9WgXcQ")
    if not success:
        print("Failed to load video")
        return
    
    # Generate study materials
    study_guide = handler.generate_study_guide()
    flashcards = handler.generate_flashcards(20)
    
    # Interactive chat
    response = handler.get_response("What is the main theme?")
    print(f"AI: {response}")
```

### Custom Study Guide Generation

```python
from backend.study_guide_generator import StudyGuideGenerator

def create_custom_study_guide(transcript: str, video_info: dict):
    generator = StudyGuideGenerator()
    
    # Generate comprehensive guide
    full_guide = generator.generate_comprehensive_study_guide(
        video_id="custom_001",
        transcript_text=transcript,
        video_info=video_info
    )
    
    # Generate specific components
    flashcards = generator.generate_flashcards(
        video_id="custom_001",
        transcript_text=transcript,
        video_info=video_info,
        num_cards=25
    )
    
    return {
        'study_guide': full_guide,
        'flashcards': flashcards
    }
```

### Vector Search Operations

```python
from backend.vector_manager import VectorManager
from backend.database import DatabaseManager

def advanced_search():
    db_manager = DatabaseManager()
    vector_manager = VectorManager(db_manager)
    
    # Process new video
    vector_manager.process_video_transcript(
        video_id="abc123",
        transcript_text="Your transcript here...",
        video_info={'title': 'Example Video'}
    )
    
    # Search with context
    response, context = vector_manager.query_transcript_with_context(
        video_id="abc123",
        question="What are the key takeaways?",
        k=5
    )
    
    return response, context
```