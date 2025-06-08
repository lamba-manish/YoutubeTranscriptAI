# API Documentation - Advanced RAG Implementation

This document provides comprehensive API documentation for the YouTube Transcript Chat AI application featuring industry-standard RAG (Retrieval-Augmented Generation) architecture.

## Overview

The application provides a modular backend API with advanced RAG capabilities including semantic chunking, multi-query retrieval, document reranking, and intelligent quality monitoring for processing YouTube video transcripts and generating high-quality AI responses.

## Advanced RAG Architecture

### AdvancedRAGSystem

The core RAG implementation featuring industry best practices.

#### Initialization
```python
from backend.advanced_rag import AdvancedRAGSystem
from backend.database import DatabaseManager

db_manager = DatabaseManager()
rag_system = AdvancedRAGSystem(db_manager)
```

#### Key Features
- **Semantic Chunking**: 800-character chunks with 200-character overlap
- **Multi-Query Retrieval**: Query expansion for comprehensive search
- **Document Reranking**: AI-powered relevance scoring
- **Quality Monitoring**: Automatic detection of low-quality embeddings

#### Methods

##### `process_video_transcript(video_id: str, transcript_text: str, video_info: dict) -> bool`
Processes transcript using advanced semantic chunking and creates high-quality embeddings.

**Parameters:**
- `video_id` (str): YouTube video ID (11 characters)
- `transcript_text` (str): Video transcript with timestamps
- `video_info` (dict): Video metadata including title, channel, duration

**Returns:**
- `bool`: True if processing successful, False otherwise

**Features:**
- Intelligent timestamp extraction and preservation
- Semantic-aware text chunking with overlap
- Batch embedding generation for efficiency
- Automatic quality threshold enforcement

**Example:**
```python
success = rag_system.process_video_transcript(
    "dQw4w9WgXcQ", 
    "[00:12] Hello world...", 
    {"title": "Example Video", "channel": "Test Channel"}
)
```

##### `retrieve_and_answer(video_id: str, question: str) -> Tuple[str, str, List[str]]`
Advanced retrieval with query expansion, multi-vector search, and document reranking.

**Parameters:**
- `video_id` (str): YouTube video ID
- `question` (str): User question about video content

**Returns:**
- `tuple`: (response, context, sources) with detailed citations

**Advanced Features:**
- Query expansion for lyrics, quotes, and content requests
- Hybrid semantic and keyword search
- Document reranking based on relevance scoring
- Source citation with timestamp references

**Example:**
```python
response, context, sources = rag_system.retrieve_and_answer(
    "dQw4w9WgXcQ", 
    "What are the lyrics in the chorus?"
)
print(f"Response: {response}")
print(f"Sources: {sources}")
```

### Enhanced Chat Handler

Main interface integrating advanced RAG with conversation management.

#### Initialization
```python
from backend.enhanced_chat_handler import EnhancedChatHandler

handler = EnhancedChatHandler()
```

#### Methods

##### `load_video(video_id: str, transcript_text: str = None, video_info: dict = None) -> bool`
Loads video with intelligent quality detection and automatic embedding regeneration.

**Quality Monitoring:**
- Detects embeddings with < 10 chunks as low quality
- Automatically regenerates poor-quality embeddings
- Progress tracking with user feedback

**Example:**
```python
success = handler.load_video("dQw4w9WgXcQ")
# Automatically detects if existing embeddings are low quality
# Regenerates with advanced RAG if needed
```

##### `get_response(user_question: str, chat_history: list = None) -> str`
Generates AI response using advanced RAG system with evaluation.

**Advanced Features:**
- Multi-stage retrieval with query expansion
- Document reranking for relevance
- Response quality evaluation with faithfulness scoring
- Comprehensive error handling and fallbacks

**Quality Metrics:**
- Faithfulness score (0.0-1.0)
- Relevance assessment
- Completeness evaluation
- Clarity measurement

## Configuration

### RAG System Configuration
```python
# Text Splitting Configuration
CHUNK_SIZE = 800                    # Optimal for semantic coherence
CHUNK_OVERLAP = 200                 # 25% overlap for context preservation

# Embedding Configuration
EMBEDDING_MODEL = "text-embedding-3-large"    # OpenAI's latest model
BATCH_SIZE = 50                               # Embedding batch processing

# Retrieval Configuration
SIMILARITY_SEARCH_K = 8             # Initial retrieval count
RERANK_TOP_K = 6                    # Final document count
QUERY_EXPANSION_ENABLED = True      # Multi-query retrieval

# Quality Thresholds
MIN_CHUNKS_THRESHOLD = 10           # Minimum chunks for quality
LOW_FAITHFULNESS_THRESHOLD = 0.7    # Response quality alert
```

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional Advanced Configuration
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=200
RAG_EMBEDDING_MODEL=text-embedding-3-large
RAG_CHAT_MODEL=gpt-4o
RAG_TEMPERATURE=0.1
```

## Data Models

### Advanced RAG Document Model
```python
{
    "page_content": "[02:30] Never gonna give you up, never gonna let you down...",
    "metadata": {
        "video_id": "dQw4w9WgXcQ",
        "chunk_index": 25,
        "chunk_type": "timestamped",
        "start_timestamp": "02:30",
        "end_timestamp": "02:45",
        "timestamp_count": 3,
        "word_count": 24,
        "char_count": 156
    }
}
```

### Enhanced Response Model
```python
{
    "response": "The lyrics from 2:30 to 3:00 are: 'Never gonna give you up...'",
    "context": "Retrieved from 6 relevant segments",
    "sources": [
        "[1] Chunk 25 (02:30-02:45)",
        "[2] Chunk 26 (02:45-03:00)"
    ],
    "evaluation": {
        "faithfulness": 0.95,
        "relevance": 0.92,
        "overall_grade": "A"
    },
    "processing_time": 1.2
}
```

## Usage Examples

### Complete Advanced RAG Workflow
```python
from backend.enhanced_chat_handler import EnhancedChatHandler

# Initialize with advanced RAG
handler = EnhancedChatHandler()

# Load video with quality monitoring
video_id = "dQw4w9WgXcQ"
success = handler.load_video(video_id)

if success:
    # Advanced query with lyrics request
    response = handler.get_response(
        "Can you give me the complete lyrics from the chorus?"
    )
    
    # The advanced RAG system will:
    # 1. Expand query to include variations
    # 2. Retrieve relevant chunks with timestamps
    # 3. Rerank for optimal relevance
    # 4. Generate response with citations
    # 5. Evaluate response quality
    
    print(f"Response: {response}")
```

### Quality Monitoring Example
```python
# Load video with automatic quality detection
handler = EnhancedChatHandler()

# System automatically detects low-quality embeddings
success = handler.load_video("video_with_poor_embeddings")

# Advanced RAG regenerates high-quality embeddings
# Progress: "Generating high-quality embeddings for AI chat..."
# Result: "Advanced RAG - Created 45 semantic chunks"
```

## Performance Metrics

### Processing Performance
```python
{
    "video_length": "3:32",
    "transcript_words": 456,
    "chunk_count": 8,
    "embedding_generation_time": 2.3,
    "total_processing_time": 3.1,
    "memory_usage_mb": 45.2
}
```

### Query Performance
```python
{
    "query": "What are the lyrics?",
    "retrieval_time": 0.15,
    "reranking_time": 0.08,
    "response_generation_time": 1.2,
    "total_response_time": 1.43,
    "documents_retrieved": 8,
    "documents_reranked": 6,
    "faithfulness_score": 0.95
}
```

## Best Practices

### Optimal Query Formulation
```python
# Effective queries for advanced RAG
queries = [
    "What are the exact lyrics from 2:30 to 3:00?",           # Specific timestamps
    "Can you quote what he said about artificial intelligence?", # Exact quotes
    "Give me the complete lyrics of the chorus",               # Complete sections
    "What are the main points discussed in this video?",       # Comprehensive summaries
]
```

### Performance Optimization
- Use specific timestamps for precise content retrieval
- Request complete sections rather than fragments
- Leverage the system's automatic quality detection
- Monitor evaluation scores for response quality assessment

### Quality Assurance
- Faithfulness scores above 0.8 indicate high-quality responses
- Automatic regeneration ensures optimal embedding quality
- Multi-query retrieval maximizes content coverage
- Document reranking improves answer relevance