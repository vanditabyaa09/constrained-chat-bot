"""Agent Module - Orchestrates the PDF QA pipeline"""

import os
from typing import List, Tuple, Optional
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.pdf_processor import PDFProcessor
from app.embedder import Embedder
from app.retriever import FAISSRetriever


class PDFAgent:
    """Orchestrates the full PDF conversational AI pipeline"""
    
    MODEL_ENDPOINT = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct"
    RELEVANCE_THRESHOLD = 0.45
    MAX_HISTORY_TURNS = 4  # Keep last 4 turns for context
    
    SYSTEM_PROMPT = """You are a precise document assistant. Answer ONLY using the context provided below. 
Do not use any outside knowledge. If the context does not contain the answer, say 
'The document does not contain information about this.' 
Always end your answer with a citation in this format: [Page X]"""
    
    OUT_OF_SCOPE_RESPONSE = "I can only answer questions based on the uploaded PDF. This question appears to be outside its scope."
    
    def __init__(self, hf_api_token: str):
        """
        Initialize PDF Agent
        
        Args:
            hf_api_token: HuggingFace API token for inference
        """
        if not hf_api_token:
            raise ValueError("HF_API_TOKEN cannot be empty")
        
        self.hf_api_token = hf_api_token
        self.embedder = Embedder()
        self.retriever: Optional[FAISSRetriever] = None
        self.pdf_processor = PDFProcessor()
        self.conversation_history: List[Tuple[str, str]] = []
        
        # Initialize LLM
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize ChatHuggingFace for conversational task"""
        llm = HuggingFaceEndpoint(
            repo_id="Qwen/Qwen2.5-7B-Instruct",
            huggingfacehub_api_token=self.hf_api_token,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.95,
            top_k=10
        )
        return ChatHuggingFace(llm=llm)
    
    def load_pdf(self, file_path: str) -> str:
        """
        Load a PDF file and build retrieval index
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Status message
        """
        try:
            # Process PDF
            chunks = self.pdf_processor.load_pdf(file_path)
            
            # Generate embeddings
            embeddings = self.embedder.embed_chunks(chunks)
            
            # Build retriever
            self.retriever = FAISSRetriever(chunks, embeddings)
            
            # Reset conversation history for new document
            self.conversation_history = []
            
            # Get metadata for response
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            
            return {
                "filename": os.path.basename(file_path),
                "pages": len(reader.pages),
                "chunks": len(chunks),
                "status": "ready"
            }
        
        except Exception as e:
            raise RuntimeError(f"Error loading PDF: {str(e)}")
    
    def _get_context_window(self) -> List[Tuple[str, str]]:
        """Get the last 4 turns from conversation history for context"""
        return self.conversation_history[-self.MAX_HISTORY_TURNS:]
    
    def _build_context_from_chunks(self, chunks: List[dict]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            page = metadata.get("page", "N/A")
            text = chunk.get("text", "")
            
            context_parts.append(f"[Page {page}]\n{text}")
        
        return "\n\n".join(context_parts)
    
    def chat(self, query: str, history: list = None) -> dict:
        """
        Answer a user query based on PDF context
        
        Args:
            query: User query string
            history: Optional list of past messages to override internal history
            
        Returns:
            Dict containing answer, citations, and in_scope status
        """
        if self.retriever is None:
            return {"answer": "Please load a PDF first.", "citations": [], "in_scope": False}
        
        # Override internal history if provided (format expected: [{"role": "user", "content": "..."}, ...])
        if history is not None:
            self.conversation_history = []
            for i in range(0, len(history) - 1, 2):
                if i + 1 < len(history):
                    self.conversation_history.append((history[i]["content"], history[i+1]["content"]))

        try:
            # Embed the query
            query_embedding = self.embedder.embed_query(query)
            
            # Retrieve top-5 chunks
            retrieved_chunks = self.retriever.retrieve(query_embedding, top_k=5)
            
            if not retrieved_chunks:
                return {"answer": self.OUT_OF_SCOPE_RESPONSE, "citations": [], "in_scope": False}
            
            # Check relevance
            best_score = retrieved_chunks[0].get("similarity_score", 0)
            if not self.retriever.is_relevant(best_score, self.RELEVANCE_THRESHOLD):
                return {"answer": self.OUT_OF_SCOPE_RESPONSE, "citations": [], "in_scope": False}
            
            # Build context from chunks
            context = self._build_context_from_chunks(retrieved_chunks)
            
            # Extract citations (unique page numbers)
            citations = sorted(list(set(chunk.get("metadata", {}).get("page") for chunk in retrieved_chunks if chunk.get("metadata", {}).get("page"))))
            
            # Build messages for ChatHuggingFace
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT)
            ]
            
            # Include recent history
            for prev_query, prev_response in self._get_context_window():
                messages.append(HumanMessage(content=prev_query))
                messages.append(AIMessage(content=prev_response))
            
            # Add current context and query
            current_input = f"Context from document:\n{context}\n\nQuestion: {query}"
            messages.append(HumanMessage(content=current_input))
            
            # Call LLM
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Store in history
            self.conversation_history.append((query, response_text))
            
            return {
                "answer": response_text,
                "citations": citations,
                "in_scope": True
            }
        
        except Exception as e:
            return {"answer": f"Error processing query: {str(e)}", "citations": [], "in_scope": False}
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self) -> List[Tuple[str, str]]:
        """Get full conversation history"""
        return self.conversation_history
