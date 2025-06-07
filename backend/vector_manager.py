"""
Vector embedding manager using LangChain and FAISS
"""
import os
import pickle
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from backend.database import DatabaseManager
import streamlit as st

class VectorManager:
    """Manages vector embeddings and similarity search using LangChain"""
    
    def __init__(self, database_manager: DatabaseManager):
        self.db_manager = database_manager
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Smaller chunks for better granularity
            chunk_overlap=100,  # Reasonable overlap
            separators=["\n\n", "\n", ". ", " ", ""],  # Better splitting on natural boundaries
            length_function=len
        )
        
        # Create prompt template for QA
        self.prompt_template = PromptTemplate(
            template="""You are an expert video content analyzer. Use ONLY the provided transcript context to answer questions.

CONTEXT from video transcript:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Answer based strictly on the transcript content provided above
- Include specific timestamps when they appear in the context
- If asking about lyrics, quotes, or specific content, provide the exact text from the transcript
- If the context doesn't contain enough information, clearly state what information is missing
- Be specific and detailed when the transcript provides the information
- For song lyrics, provide the complete text as it appears in the transcript

ANSWER:""",
            input_variables=['context', 'question']
        )
    
    def process_video_transcript(self, video_id: str, transcript_text: str, video_info: dict) -> bool:
        """
        Process and store video transcript with embeddings
        """
        try:
            print(f"Debug - Processing transcript for video {video_id}")
            
            # Check if already processed
            if self.db_manager.embeddings_exist(video_id):
                print(f"Debug - Embeddings already exist for {video_id}")
                return True
            
            # Split transcript into chunks
            documents = self.text_splitter.create_documents([transcript_text])
            print(f"Debug - Created {len(documents)} chunks")
            
            # Generate embeddings for each chunk
            chunks_with_embeddings = []
            for i, doc in enumerate(documents):
                try:
                    # Generate embedding for this chunk
                    embedding = self.embeddings.embed_query(doc.page_content)
                    chunks_with_embeddings.append((doc.page_content, embedding))
                    
                    if (i + 1) % 10 == 0:
                        print(f"Debug - Processed {i + 1}/{len(documents)} chunks")
                        
                except Exception as e:
                    print(f"Debug - Error embedding chunk {i}: {str(e)}")
                    continue
            
            # Save to database
            self.db_manager.save_embeddings(video_id, chunks_with_embeddings)
            print(f"Debug - Saved {len(chunks_with_embeddings)} embeddings to database")
            
            return True
            
        except Exception as e:
            print(f"Debug - Error processing transcript: {str(e)}")
            return False
    
    def create_vector_store(self, video_id: str) -> FAISS:
        """
        Create FAISS vector store from stored embeddings
        """
        try:
            # Get embeddings from database
            embeddings_data = self.db_manager.get_embeddings(video_id)
            
            if not embeddings_data:
                print(f"Debug - No embeddings found for video {video_id}")
                raise Exception(f"No vector embeddings found for video {video_id}")
            
            print(f"Debug - Loading {len(embeddings_data)} embeddings from database")
            
            # Create documents and embeddings lists
            documents = []
            embeddings_list = []
            
            for item in embeddings_data:
                doc = Document(
                    page_content=item['chunk_text'],
                    metadata={'video_id': video_id, 'chunk_index': item['chunk_index']}
                )
                documents.append(doc)
                embeddings_list.append(item['embedding'])
            
            # Create FAISS vector store
            vector_store = FAISS.from_texts(
                texts=[doc.page_content for doc in documents],
                embedding=self.embeddings,
                metadatas=[doc.metadata for doc in documents]
            )
            
            print(f"Debug - Created FAISS vector store with {len(documents)} documents")
            return vector_store
            
        except Exception as e:
            print(f"Debug - Error creating vector store: {str(e)}")
            return None
    
    def query_transcript_with_context(self, video_id: str, question: str, k: int = 4) -> tuple[str, str]:
        """
        Query transcript using vector similarity search and return both response and context
        """
        try:
            # Create vector store
            vector_store = self.create_vector_store(video_id)
            if not vector_store:
                return "No vector embeddings found for this video.", ""
            
            # Perform similarity search
            docs = vector_store.similarity_search(question, k=k)
            
            if not docs:
                return "No relevant content found for your question.", ""
            
            # Combine retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create QA chain with improved retrieval parameters
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(
                    search_type="similarity_score_threshold",
                    search_kwargs={
                        "k": k * 2,  # Retrieve more documents initially
                        "score_threshold": 0.3  # Lower threshold for more inclusive search
                    }
                ),
                return_source_documents=True,
                chain_type_kwargs={"prompt": self.prompt_template}
            )
            
            # Get response
            result = qa_chain({"query": question})
            response = result["result"]
            
            # Add citations to response
            citations = self._generate_citations(docs)
            response_with_citations = f"{response}\n\n**Sources:**\n{citations}"
            
            return response_with_citations, context
            
        except Exception as e:
            print(f"Debug - Error querying transcript: {str(e)}")
            # Try to provide a fallback response
            error_msg = "No vector embeddings found for this video."
            if "embeddings" in str(e).lower() or "vector" in str(e).lower():
                error_msg += " Please try generating the study tools first, which will create the necessary embeddings for chat functionality."
            return error_msg, ""

    def query_transcript(self, video_id: str, question: str, k: int = 4) -> str:
        """
        Query transcript using vector similarity search
        """
        try:
            # Create vector store
            vector_store = self.create_vector_store(video_id)
            if not vector_store:
                return "Sorry, I couldn't access the video transcript data."
            
            # Create retriever
            retriever = vector_store.as_retriever(
                search_type="similarity", 
                search_kwargs={"k": k}
            )
            
            # Retrieve relevant documents
            retrieved_docs = retriever.invoke(question)
            
            if not retrieved_docs:
                return "I couldn't find relevant information in the transcript to answer your question."
            
            # Combine context from retrieved documents
            context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
            
            # Generate response using LLM
            final_prompt = self.prompt_template.invoke({
                "context": context_text, 
                "question": question
            })
            
            response = self.llm.invoke(final_prompt)
            return response.content
            
        except Exception as e:
            print(f"Debug - Error querying transcript: {str(e)}")
            return f"Sorry, I encountered an error while processing your question: {str(e)}"
    
    def get_video_summary(self, video_id: str) -> str:
        """
        Generate a comprehensive summary of the video
        """
        try:
            # Get all chunks to create a comprehensive summary
            vector_store = self.create_vector_store(video_id)
            if not vector_store:
                return "Sorry, I couldn't access the video transcript data."
            
            # Get video info from database
            video_data = self.db_manager.get_video_transcript(video_id)
            if not video_data:
                return "Video information not found."
            
            # Use first few chunks for summary (to stay within token limits)
            embeddings_data = self.db_manager.get_embeddings(video_id)
            if not embeddings_data:
                return "No transcript data available for summary."
            
            # Take first 5 chunks for summary
            summary_chunks = embeddings_data[:5]
            context_text = "\n\n".join(chunk['chunk_text'] for chunk in summary_chunks)
            
            summary_prompt = f"""
            Please provide a comprehensive summary of this YouTube video based on the transcript content below.
            Include the main topics, key points, and important insights discussed.
            
            Video Title: {video_data.get('title', 'Unknown')}
            Channel: {video_data.get('channel', 'Unknown')}
            
            Transcript Content:
            {context_text}
            
            Please provide a well-structured summary:
            """
            
            response = self.llm.invoke(summary_prompt)
            return response.content
            
        except Exception as e:
            print(f"Debug - Error generating summary: {str(e)}")
            return f"Sorry, I encountered an error while generating the summary: {str(e)}"
    
    def _generate_citations(self, docs) -> str:
        """Generate citations from retrieved documents"""
        citations = []
        for i, doc in enumerate(docs, 1):
            # Extract timestamp if available from metadata
            timestamp = doc.metadata.get('timestamp', 'Unknown time')
            preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            citations.append(f"[{i}] {timestamp}: \"{preview}\"")
        
        return "\n".join(citations)
    
    def extract_highlight_reel(self, video_id: str, num_highlights: int = 5) -> str:
        """Extract key moments/highlights from the video transcript"""
        try:
            # Get video data
            video_data = self.db_manager.get_video_transcript(video_id)
            if not video_data:
                return "No video transcript found."
            
            # Handle both dict and object formats
            if isinstance(video_data, dict):
                transcript_text = video_data.get('transcript', video_data.get('transcript_text', ''))
                title = video_data.get('title', 'Unknown')
            else:
                transcript_text = video_data.transcript_text
                title = video_data.title or 'Unknown'
            
            highlight_prompt = f"""
            Analyze this YouTube video transcript and extract {num_highlights} key highlights or important moments.
            For each highlight, provide:
            1. A brief title/description
            2. The key quote or content
            3. Why it's significant
            
            Video Title: {title}
            
            Transcript:
            {transcript_text[:5000]}...
            
            Format your response as:
            **Highlight 1: [Title]**
            Quote: "[Key quote]"
            Significance: [Why this moment is important]
            
            **Highlight 2: [Title]**
            ...
            """
            
            response = self.llm.invoke(highlight_prompt)
            return response.content
            
        except Exception as e:
            print(f"Debug - Error extracting highlights: {str(e)}")
            return f"Error extracting highlights: {str(e)}"
    
    def analyze_video_mood(self, video_id: str) -> str:
        """Analyze the overall mood and tone of the video"""
        try:
            # Get video data
            video_data = self.db_manager.get_video_transcript(video_id)
            if not video_data:
                return "No video transcript found."
            
            # Handle both dict and object formats
            if isinstance(video_data, dict):
                transcript_text = video_data.get('transcript', video_data.get('transcript_text', ''))
                title = video_data.get('title', 'Unknown')
                channel = video_data.get('channel', 'Unknown')
            else:
                transcript_text = video_data.transcript_text
                title = video_data.title or 'Unknown'
                channel = video_data.channel or 'Unknown'
            
            mood_prompt = f"""
            Analyze the overall mood, tone, and emotional characteristics of this YouTube video based on its transcript.
            
            Video Title: {title}
            Channel: {channel}
            
            Transcript:
            {transcript_text[:4000]}...
            
            Please provide:
            1. **Overall Mood**: (e.g., Educational, Entertaining, Serious, Humorous, Inspirational, etc.)
            2. **Tone**: (e.g., Casual, Professional, Energetic, Calm, etc.)
            3. **Emotional Characteristics**: What emotions does the content evoke?
            4. **Target Audience Feel**: How would viewers likely feel watching this?
            5. **Content Style**: (e.g., Tutorial, Commentary, Review, Storytelling, etc.)
            
            Provide a detailed analysis with specific examples from the transcript.
            """
            
            response = self.llm.invoke(mood_prompt)
            return response.content
            
        except Exception as e:
            print(f"Debug - Error analyzing mood: {str(e)}")
            return f"Error analyzing video mood: {str(e)}"