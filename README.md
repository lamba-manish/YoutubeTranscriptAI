# YouTube Transcript Chat AI

A Streamlit-based application that extracts YouTube video transcripts and enables AI-powered conversations about video content using vector embeddings and database persistence.

## Features

- **YouTube Transcript Extraction**: Automatically extracts transcripts from YouTube videos
- **AI-Powered Chat**: Interact with video content using OpenAI's GPT models
- **Vector Search**: Uses FAISS vector embeddings for intelligent transcript search
- **Database Persistence**: SQLite/PostgreSQL database for storing transcripts and embeddings
- **Modern UI**: YouTube-inspired dark theme interface
- **Docker Support**: Containerized deployment for scalability

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API Key
- Docker (optional)

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd youtube-transcript-chat-ai
```

2. Install dependencies:
```bash
pip install uv
uv sync
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

4. Run the application:
```bash
streamlit run app.py --server.port 5000
```

### Docker Deployment

1. Build and run with Docker Compose:
```bash
# Basic deployment with SQLite
docker-compose up --build

# Production deployment with PostgreSQL
docker-compose --profile postgres up --build
```

2. Access the application at `http://localhost:5000`

## Usage

1. **Enter Video ID**: Input an 11-character YouTube video ID (e.g., `dQw4w9WgXcQ`)
2. **Load Video**: Click "Load Video" to extract and process the transcript
3. **Start Chatting**: Ask questions about the video content using natural language

### Example Video IDs

- `Gfr50f6ZBvo` - Podcast Interview (long-form conversation)
- `dQw4w9WgXcQ` - Rick Astley - Never Gonna Give You Up
- `9bZkp7q19f0` - TED Talk example

### Example Questions

- "What are the main points discussed in this video?"
- "Can you summarize the key takeaways?"
- "What does the speaker say about [specific topic]?"
- "At what time is [specific topic] mentioned?"

## Architecture

### Backend Components

- **Database Layer** (`backend/database.py`): SQLAlchemy models for video transcripts and embeddings
- **Vector Manager** (`backend/vector_manager.py`): FAISS vector store management using LangChain
- **Enhanced Chat Handler** (`backend/enhanced_chat_handler.py`): AI chat with vector search integration

### Key Technologies

- **Streamlit**: Web interface framework
- **LangChain**: Document processing and AI chains
- **FAISS**: Vector similarity search
- **OpenAI**: GPT models for chat responses
- **SQLAlchemy**: Database ORM
- **YouTube Transcript API**: Transcript extraction

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)

### Docker Environment

The application includes production-ready Docker configuration:

- **Dockerfile**: Multi-stage build with Python 3.11
- **docker-compose.yml**: Service orchestration with optional PostgreSQL
- **Health checks**: Built-in application health monitoring

## Development

### Project Structure

```
youtube-transcript-chat-ai/
├── app.py                          # Main Streamlit application
├── backend/
│   ├── __init__.py
│   ├── database.py                 # Database models and manager
│   ├── enhanced_chat_handler.py    # AI chat with vector search
│   └── vector_manager.py           # FAISS vector operations
├── youtube_utils.py                # YouTube transcript extraction
├── chat_handler.py                 # Legacy chat handler
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── Dockerfile                      # Container build instructions
├── docker-compose.yml              # Service orchestration
└── pyproject.toml                  # Python dependencies
```

### Key Features

1. **Intelligent Transcript Processing**: Chunks transcripts into optimally-sized segments with overlap
2. **Vector Embeddings**: Creates searchable embeddings using OpenAI's text-embedding models
3. **Database Persistence**: Avoids reprocessing by storing transcripts and embeddings
4. **Smart Context Retrieval**: Uses vector similarity to find relevant transcript sections
5. **Modern UI**: YouTube-inspired design with responsive layout

## API Integration

The application integrates with:

- **OpenAI API**: For chat completions and text embeddings
- **YouTube oEmbed API**: For video metadata extraction
- **YouTube Transcript API**: For caption/transcript extraction

## Deployment Options

### Development
- Local Streamlit server on port 5000
- SQLite database for simplicity

### Production
- Docker container deployment
- PostgreSQL database for scalability
- Health checks and auto-restart
- Volume persistence for data

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues or questions, please create an issue in the repository or contact the development team.