"""Embedding Module - Generate embeddings for text content using sentence-transformers"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np


class Embedder:
    """Generate embeddings locally using HuggingFace sentence-transformers (BGE model)"""
    
    MODEL_NAME = "BAAI/bge-small-en-v1.5"
    QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "
    
    def __init__(self):
        """Initialize embedder with BGE model from sentence-transformers"""
        self.model = SentenceTransformer(self.MODEL_NAME)
    
    def embed_chunks(self, chunks: List[Dict]) -> np.ndarray:
        """
        Generate embeddings for document chunks
        
        Args:
            chunks: List of chunk dictionaries with 'text' key
            
        Returns:
            NumPy array of normalized embeddings with shape (len(chunks), embedding_dim)
        """
        if not chunks:
            raise ValueError("Chunks list cannot be empty")
        
        # Extract text from chunks
        texts = [chunk.get("text", "") for chunk in chunks]
        
        if not texts or all(not text for text in texts):
            raise ValueError("All chunks must contain non-empty 'text' field")
        
        # Encode texts locally with normalization
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        return embeddings
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query with instruction prefix
        
        Args:
            query: Query string to embed
            
        Returns:
            Normalized NumPy array of shape (embedding_dim,)
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        # Add instruction prefix as required by BGE models
        prefixed_query = self.QUERY_INSTRUCTION + query
        
        # Encode with normalization
        embedding = self.model.encode(
            [prefixed_query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        return embedding[0]
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by the model
        
        Returns:
            Embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()
