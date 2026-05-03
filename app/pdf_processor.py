"""PDF Processing Module - Extract text from PDF files with chunking"""

from pypdf import PdfReader
from pathlib import Path
from typing import List, Dict


class PDFProcessor:
    """Process PDF files and extract text content with sliding window chunking"""
    
    # Chunking parameters
    CHUNK_SIZE = 500  # characters per chunk
    CHUNK_OVERLAP = 50  # character overlap between chunks
    
    def __init__(self):
        """Initialize PDF processor"""
        self.documents = []
    
    def _chunk_text(self, text: str, page_num: int, filename: str) -> List[Dict]:
        """
        Split text into overlapping chunks using sliding window approach
        
        Args:
            text: Text content to chunk
            page_num: Page number (1-indexed)
            filename: Source filename
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        
        if not text or len(text) == 0:
            return chunks
        
        # Sliding window chunking
        chunk_index = 0
        start_idx = 0
        
        while start_idx < len(text):
            # Define chunk end position
            end_idx = min(start_idx + self.CHUNK_SIZE, len(text))
            
            # Extract chunk
            chunk_text = text[start_idx:end_idx].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "page": page_num,
                        "chunk_index": chunk_index,
                        "source": filename
                    }
                })
                chunk_index += 1
            
            # Move start position for next iteration (with overlap)
            # If this is the last chunk, we're done
            if end_idx >= len(text):
                break
            
            start_idx = end_idx - self.CHUNK_OVERLAP
        
        return chunks
    
    def load_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Load and process a PDF file with text chunking
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of chunk dictionaries with 'text' and 'metadata' keys
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a PDF
            RuntimeError: If PDF processing fails
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF: {pdf_path}")
        
        chunks = []
        
        try:
            reader = PdfReader(pdf_path)
            filename = pdf_path.name
            
            # Extract and chunk text from each page
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                
                # Chunk the page text
                page_chunks = self._chunk_text(
                    text=text,
                    page_num=page_num + 1,  # 1-indexed page numbers
                    filename=filename
                )
                chunks.extend(page_chunks)
            
            self.documents = chunks
            
        except Exception as e:
            raise RuntimeError(f"Error processing PDF: {str(e)}")
        
        return chunks
    
    def get_documents(self) -> List[Dict]:
        """
        Get all loaded document chunks
        
        Returns:
            List of chunk dictionaries
        """
        return self.documents
    
    def clear_documents(self):
        """Clear all loaded document chunks"""
        self.documents = []
