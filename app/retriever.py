"""Retriever Module - Vector storage and retrieval using FAISS with normalized embeddings"""

import faiss
import numpy as np
from typing import List, Dict


class FAISSRetriever:
    """Retrieve relevant chunks using FAISS with inner product similarity on normalized embeddings"""
    
    def __init__(self, chunks: List[Dict], embeddings: np.ndarray):
        """
        Initialize retriever with chunks and their embeddings
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata' keys
            embeddings: NumPy array of normalized embeddings with shape (len(chunks), embedding_dim)
                       Embeddings should be normalized (L2 norm = 1) for cosine similarity
        """
        if not chunks:
            raise ValueError("Chunks list cannot be empty")
        
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        if embeddings.shape[1] == 0:
            raise ValueError("Embeddings must have non-zero dimension")
        
        self.chunks = chunks
        self.embeddings = embeddings.astype('float32')
        
        # Build FAISS IndexFlatIP (inner product)
        # On normalized embeddings, inner product equals cosine similarity
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(self.embeddings)
    
    def retrieve(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """
        Retrieve top-k most relevant chunks for a query embedding
        
        Args:
            query_embedding: Normalized query embedding of shape (embedding_dim,)
            top_k: Number of chunks to retrieve
            
        Returns:
            List of chunk dictionaries with added 'similarity_score' field
            
        Raises:
            ValueError: If query embedding has wrong shape or is empty
        """
        if query_embedding.ndim != 1:
            raise ValueError("Query embedding must be 1-dimensional")
        
        if query_embedding.shape[0] != self.embeddings.shape[1]:
            raise ValueError(
                f"Query embedding dimension {query_embedding.shape[0]} "
                f"does not match index dimension {self.embeddings.shape[1]}"
            )
        
        # Prepare query embedding for FAISS (must be 2D)
        query_embedding = np.array([query_embedding], dtype='float32')
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Build results with metadata and scores
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk["similarity_score"] = float(score)
                results.append(chunk)
        
        return results
    
    def is_relevant(self, score: float, threshold: float = 0.45) -> bool:
        """
        Check if a similarity score indicates a relevant match
        
        Args:
            score: Similarity score from retrieval (inner product on normalized embeddings)
            threshold: Minimum similarity threshold for relevance
            
        Returns:
            True if score >= threshold, False otherwise
        """
        return score >= threshold
    
    def get_chunks(self) -> List[Dict]:
        """Get all indexed chunks"""
        return self.chunks
    
    def get_chunk_count(self) -> int:
        """Get the number of indexed chunks"""
        return len(self.chunks)
