"""
Database models and configuration for YouTube Transcript Chat AI
"""
import os
import pickle
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, LargeBinary, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class VideoTranscript(Base):
    """Model for storing video transcripts and metadata"""
    __tablename__ = 'video_transcripts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(String(11), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=True)
    channel = Column(String(200), nullable=True)
    duration = Column(String(50), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    transcript_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VectorEmbedding(Base):
    """Model for storing vector embeddings"""
    __tablename__ = 'vector_embeddings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(String(11), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding_data = Column(LargeBinary, nullable=False)  # Pickled embedding vector
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Database manager for handling database operations"""
    
    def __init__(self, database_url=None):
        if database_url is None:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///backend/youtube_transcripts.db')
        
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def video_exists(self, video_id: str) -> bool:
        """Check if video transcript already exists in database"""
        with self.get_session() as session:
            result = session.query(VideoTranscript).filter_by(video_id=video_id).first()
            return result is not None
    
    def save_video_transcript(self, video_id: str, transcript_text: str, video_info: dict):
        """Save video transcript and metadata to database"""
        with self.get_session() as session:
            # Check if already exists
            existing = session.query(VideoTranscript).filter_by(video_id=video_id).first()
            
            if existing:
                # Update existing record
                existing.transcript_text = transcript_text
                existing.title = video_info.get('title')
                existing.channel = video_info.get('channel')
                existing.duration = video_info.get('duration')
                existing.thumbnail_url = video_info.get('thumbnail')
                existing.updated_at = datetime.utcnow()
            else:
                # Create new record
                video_transcript = VideoTranscript(
                    video_id=video_id,
                    title=video_info.get('title'),
                    channel=video_info.get('channel'),
                    duration=video_info.get('duration'),
                    thumbnail_url=video_info.get('thumbnail'),
                    transcript_text=transcript_text
                )
                session.add(video_transcript)
            
            session.commit()
    
    def get_video_transcript(self, video_id: str):
        """Retrieve video transcript and metadata from database"""
        with self.get_session() as session:
            result = session.query(VideoTranscript).filter_by(video_id=video_id).first()
            if result:
                return {
                    'video_id': result.video_id,
                    'title': result.title,
                    'channel': result.channel,
                    'duration': result.duration,
                    'thumbnail': result.thumbnail_url,
                    'transcript_text': result.transcript_text,
                    'created_at': result.created_at,
                    'updated_at': result.updated_at
                }
            return None
    
    def save_embeddings(self, video_id: str, chunks_with_embeddings: list):
        """Save vector embeddings for a video"""
        with self.get_session() as session:
            # Delete existing embeddings for this video
            session.query(VectorEmbedding).filter_by(video_id=video_id).delete()
            
            # Save new embeddings
            for i, (chunk_text, embedding_vector) in enumerate(chunks_with_embeddings):
                embedding_data = pickle.dumps(embedding_vector)
                vector_embedding = VectorEmbedding(
                    video_id=video_id,
                    chunk_index=i,
                    chunk_text=chunk_text,
                    embedding_data=embedding_data
                )
                session.add(vector_embedding)
            
            session.commit()
    
    def get_embeddings(self, video_id: str):
        """Retrieve vector embeddings for a video"""
        with self.get_session() as session:
            results = session.query(VectorEmbedding).filter_by(video_id=video_id).order_by(VectorEmbedding.chunk_index).all()
            embeddings = []
            for result in results:
                embedding_vector = pickle.loads(result.embedding_data)
                embeddings.append({
                    'chunk_text': result.chunk_text,
                    'embedding': embedding_vector,
                    'chunk_index': result.chunk_index
                })
            return embeddings
    
    def embeddings_exist(self, video_id: str) -> bool:
        """Check if embeddings exist for a video"""
        with self.get_session() as session:
            result = session.query(VectorEmbedding).filter_by(video_id=video_id).first()
            return result is not None
    
    def get_all_videos(self) -> list:
        """Get all videos from database with their metadata"""
        with self.get_session() as session:
            videos = session.query(VideoTranscript).order_by(VideoTranscript.created_at.desc()).all()
            return [{
                'video_id': video.video_id,
                'title': video.title,
                'channel': video.channel,
                'duration': video.duration,
                'thumbnail_url': video.thumbnail_url,
                'created_at': video.created_at.strftime('%Y-%m-%d %H:%M') if video.created_at else 'Unknown'
            } for video in videos]