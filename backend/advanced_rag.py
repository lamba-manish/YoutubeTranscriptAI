"""
Advanced RAG Implementation with Industry Best Practices
"""
import re
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import streamlit as st

class AdvancedRAGSystem:
    """
    Industry-standard RAG implementation with:
    - Semantic chunking with overlap
    - Multi-vector retrieval
    - Query expansion and rewriting
    - Context ranking and reranking
    - Hybrid search (semantic + keyword)
    """
    
    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")  # Better model
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)  # More stable temperature
        
        # Advanced text splitter with semantic awareness
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Optimal size for most models
            chunk_overlap=200,  # 25% overlap for context preservation
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ": ", " ", ""],
            length_function=len,
            is_separator_regex=False
        )
        
        # Specialized prompt for video transcript analysis
        self.qa_prompt = PromptTemplate(
            template="""You are an expert AI assistant analyzing YouTube video transcripts. Your task is to provide accurate, detailed answers based STRICTLY on the provided context.

CONTEXT (Video Transcript Segments):
{context}

USER QUESTION: {question}

ANALYSIS GUIDELINES:
1. Base your answer ONLY on the provided transcript context
2. Include specific timestamps when available (format: [MM:SS] or [HH:MM:SS])
3. For lyrics requests: Provide complete, consecutive text from transcript
4. For content requests: Quote exact phrases and provide detailed explanations
5. If context is insufficient: Clearly state what specific information is missing
6. Maintain chronological order when referencing multiple segments
7. Preserve speaker context and conversation flow

RESPONSE FORMAT:
- Start with direct answer to the question
- Include relevant timestamps and quotes
- Provide additional context when helpful
- End with source references

ANSWER:""",
            input_variables=["context", "question"]
        )
    
    def extract_timestamps(self, text: str) -> List[Tuple[str, str]]:
        """Extract timestamps and associated text for better chunking"""
        timestamp_pattern = r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]'
        segments = []
        
        parts = re.split(timestamp_pattern, text)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                timestamp = parts[i]
                content = parts[i + 1].strip()
                if content:
                    segments.append((timestamp, content))
        
        return segments
    
    def create_semantic_chunks(self, transcript_text: str, video_id: str) -> List[Document]:
        """Create semantically aware chunks with metadata"""
        # Use RecursiveCharacterTextSplitter for better chunking
        docs = self.text_splitter.create_documents([transcript_text])
        
        # Extract timestamps for each chunk and add metadata
        documents = []
        for i, doc in enumerate(docs):
            # Extract timestamps from this chunk
            timestamps = re.findall(r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]', doc.page_content)
            
            # Get start and end timestamps
            start_timestamp = timestamps[0] if timestamps else 'unknown'
            end_timestamp = timestamps[-1] if timestamps else 'unknown'
            
            # Enhanced metadata
            doc.metadata = {
                'video_id': video_id,
                'chunk_index': i,
                'chunk_type': 'timestamped' if timestamps else 'text',
                'start_timestamp': start_timestamp,
                'end_timestamp': end_timestamp,
                'timestamp_count': len(timestamps),
                'word_count': len(doc.page_content.split()),
                'char_count': len(doc.page_content)
            }
            
            documents.append(doc)
        
        print(f"Advanced RAG - Created {len(documents)} chunks with metadata")
        return documents
    
    def expand_query(self, query: str) -> List[str]:
        """Generate query variations for better retrieval"""
        # Simple query expansion - can be enhanced with language models
        expanded_queries = [query]
        
        # Add variations for common video content requests
        query_lower = query.lower()
        
        if "lyrics" in query_lower or "song" in query_lower:
            expanded_queries.extend([
                f"complete text of {query}",
                f"full lyrics {query}",
                f"song content {query}"
            ])
        
        if "quote" in query_lower or "said" in query_lower:
            expanded_queries.extend([
                f"exact words {query}",
                f"transcript {query}",
                f"mentioned {query}"
            ])
        
        return expanded_queries
    
    def rerank_documents(self, query: str, documents: List[Document], top_k: int = 6) -> List[Document]:
        """Rerank documents based on relevance scoring"""
        if not documents:
            return documents
        
        # Simple reranking based on query keywords and timestamp relevance
        scored_docs = []
        query_words = set(query.lower().split())
        
        for doc in documents:
            score = 0.0
            content_lower = doc.page_content.lower()
            
            # Keyword matching score
            content_words = set(content_lower.split())
            keyword_overlap = len(query_words.intersection(content_words))
            score += keyword_overlap * 2.0
            
            # Timestamp presence score
            if '[' in doc.page_content and ']' in doc.page_content:
                score += 1.0
            
            # Length penalty (prefer medium-length chunks)
            word_count = doc.metadata.get('word_count', 0)
            if 50 <= word_count <= 200:
                score += 0.5
            
            scored_docs.append((score, doc))
        
        # Sort by score and return top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]
    
    def process_video_transcript(self, video_id: str, transcript_text: str, video_info: dict) -> bool:
        """Process transcript with advanced chunking and store embeddings"""
        try:
            print(f"Advanced RAG - Processing transcript for video {video_id}")
            
            # Check if already processed
            if self.db_manager.embeddings_exist(video_id):
                embeddings_data = self.db_manager.get_embeddings(video_id)
                if len(embeddings_data) >= 10:  # Good quality threshold
                    print(f"Advanced RAG - High quality embeddings exist for {video_id}")
                    return True
                else:
                    print(f"Advanced RAG - Upgrading low quality embeddings for {video_id}")
            
            # Create semantic chunks
            documents = self.create_semantic_chunks(transcript_text, video_id)
            print(f"Advanced RAG - Created {len(documents)} semantic chunks")
            
            # Generate embeddings with progress tracking
            chunks_with_embeddings = []
            batch_size = 50  # Process in batches for efficiency
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                # Generate embeddings for batch
                texts = [doc.page_content for doc in batch]
                embeddings_batch = self.embeddings.embed_documents(texts)
                
                # Store with metadata
                for doc, embedding in zip(batch, embeddings_batch):
                    chunks_with_embeddings.append((doc.page_content, embedding))
                
                print(f"Advanced RAG - Processed {min(i + batch_size, len(documents))}/{len(documents)} chunks")
            
            # Clear old embeddings and save new ones
            with self.db_manager.get_session() as session:
                from backend.database import VectorEmbedding
                session.query(VectorEmbedding).filter_by(video_id=video_id).delete()
                session.commit()
            
            self.db_manager.save_embeddings(video_id, chunks_with_embeddings)
            print(f"Advanced RAG - Saved {len(chunks_with_embeddings)} high-quality embeddings")
            
            return True
            
        except Exception as e:
            print(f"Advanced RAG - Error processing transcript: {str(e)}")
            return False
    
    def retrieve_and_answer(self, video_id: str, question: str) -> Tuple[str, str, List[str]]:
        """Advanced retrieval with query expansion and reranking"""
        try:
            # Load embeddings from database
            embeddings_data = self.db_manager.get_embeddings(video_id)
            
            if not embeddings_data:
                return "No embeddings found for this video. Please generate study materials first to enable chat functionality.", "", []
            
            print(f"Advanced RAG - Loaded {len(embeddings_data)} embeddings for query")
            
            # Recreate vector store
            documents = []
            embeddings_list = []
            
            for item in embeddings_data:
                doc = Document(
                    page_content=item['chunk_text'],
                    metadata={'video_id': video_id, 'chunk_index': item['chunk_index']}
                )
                documents.append(doc)
                embeddings_list.append(item['embedding'])
            
            # Create FAISS index
            vector_store = FAISS.from_documents(
                documents, 
                self.embeddings
            )
            
            # Multi-query retrieval
            expanded_queries = self.expand_query(question)
            all_retrieved_docs = []
            
            for query in expanded_queries:
                # Retrieve with different strategies
                docs_similarity = vector_store.similarity_search(query, k=8)
                all_retrieved_docs.extend(docs_similarity)
            
            # Remove duplicates while preserving order
            seen_content = set()
            unique_docs = []
            for doc in all_retrieved_docs:
                if doc.page_content not in seen_content:
                    seen_content.add(doc.page_content)
                    unique_docs.append(doc)
            
            # Rerank documents
            final_docs = self.rerank_documents(question, unique_docs, top_k=6)
            
            if not final_docs:
                return "No relevant content found for your question. Try rephrasing or asking about different aspects of the video.", "", []
            
            # Prepare context
            context_parts = []
            sources = []
            
            for i, doc in enumerate(final_docs, 1):
                context_parts.append(f"Segment {i}:\n{doc.page_content}")
                chunk_idx = doc.metadata.get('chunk_index', 'unknown')
                sources.append(f"[{i}] Chunk {chunk_idx}")
            
            context = "\n\n".join(context_parts)
            
            # Generate response using QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(search_kwargs={"k": len(final_docs)}),
                return_source_documents=True,
                chain_type_kwargs={"prompt": self.qa_prompt}
            )
            
            result = qa_chain.invoke({"query": question})
            response = result["result"]
            
            print(f"Advanced RAG - Generated response with {len(final_docs)} source segments")
            
            return response, context, sources
            
        except Exception as e:
            error_msg = f"Advanced RAG error: {str(e)}"
            print(error_msg)
            return f"I encountered an error processing your question: {str(e)}", "", []