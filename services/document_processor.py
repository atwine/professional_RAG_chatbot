"""
Document processing service for Health AI Consultant.
Handles PDF parsing, text extraction, chunking, and vector storage.
"""
import os
import uuid
import logging
import tempfile
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# PDF processing libraries
import PyPDF2
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import our services
from services.vector_store import VectorStoreService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing documents and storing them in the vector database."""
    
    def __init__(self, 
                 chunk_size: int = 1000, 
                 chunk_overlap: int = 200):
        """
        Initialize the document processor.
        
        Args:
            chunk_size: Size of text chunks for vectorization.
            chunk_overlap: Overlap between chunks to maintain context.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_store = VectorStoreService()
        logger.info(f"Initialized document processor with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    
    def process_document(self, file_path: str, original_filename: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process a document and store it in the vector database.
        
        Args:
            file_path: Path to the document file.
            original_filename: Original name of the uploaded file.
            
        Returns:
            Tuple of document ID and metadata.
        """
        logger.info(f"Processing document: {original_filename}")
        
        # Generate a unique document ID
        document_id = str(uuid.uuid4())
        
        # Extract text and metadata from the document
        text, metadata = self._extract_text_and_metadata(file_path, original_filename)
        
        # Chunk the text
        chunks = self._chunk_text(text, metadata)
        
        # Store chunks in vector database
        self._store_chunks(document_id, chunks, metadata)
        
        # Update metadata with processing information
        metadata.update({
            "id": document_id,
            "filename": original_filename,
            "processed_at": datetime.now().isoformat(),
            "chunk_count": len(chunks)
        })
        
        logger.info(f"Document processed successfully: {document_id}")
        return document_id, metadata
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the system.
        
        Returns:
            List of document metadata.
        """
        # This would typically query the vector database or a separate document metadata store
        # For now, we'll return a placeholder
        return self.vector_store.list_documents()
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific document.
        
        Args:
            document_id: ID of the document to retrieve.
            
        Returns:
            Document metadata or None if not found.
        """
        return self.vector_store.get_document_metadata(document_id)
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the system.
        
        Args:
            document_id: ID of the document to delete.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.vector_store.delete_document(document_id)
    
    def _extract_text_and_metadata(self, file_path: str, original_filename: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text and metadata from a document.
        
        Args:
            file_path: Path to the document file.
            original_filename: Original name of the uploaded file.
            
        Returns:
            Tuple of extracted text and metadata.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(file_path, original_filename)
        elif file_ext == '.txt':
            return self._extract_from_txt(file_path, original_filename)
        elif file_ext == '.docx':
            return self._extract_from_docx(file_path, original_filename)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def _extract_from_pdf(self, file_path: str, original_filename: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text and metadata from a PDF file.
        
        Args:
            file_path: Path to the PDF file.
            original_filename: Original name of the uploaded file.
            
        Returns:
            Tuple of extracted text and metadata.
        """
        # Try PyMuPDF first as it generally has better text extraction
        try:
            doc = fitz.open(file_path)
            
            # Extract metadata
            metadata = {
                "title": doc.metadata.get("title", original_filename),
                "author": doc.metadata.get("author", "Unknown"),
                "subject": doc.metadata.get("subject", ""),
                "keywords": doc.metadata.get("keywords", ""),
                "page_count": len(doc),
                "file_type": "PDF"
            }
            
            # Extract text from each page
            full_text = ""
            for page_num, page in enumerate(doc):
                full_text += page.get_text() + f"\n\n--- Page {page_num + 1} ---\n\n"
            
            doc.close()
            return full_text, metadata
            
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed, falling back to PyPDF2: {e}")
            
            # Fall back to PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                info = reader.metadata
                metadata = {
                    "title": info.title if info.title else original_filename,
                    "author": info.author if info.author else "Unknown",
                    "subject": info.subject if info.subject else "",
                    "page_count": len(reader.pages),
                    "file_type": "PDF"
                }
                
                # Extract text from each page
                full_text = ""
                for page_num, page in enumerate(reader.pages):
                    full_text += page.extract_text() + f"\n\n--- Page {page_num + 1} ---\n\n"
                
                return full_text, metadata
    
    def _extract_from_txt(self, file_path: str, original_filename: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text and metadata from a text file.
        
        Args:
            file_path: Path to the text file.
            original_filename: Original name of the uploaded file.
            
        Returns:
            Tuple of extracted text and metadata.
        """
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            text = file.read()
        
        # Count lines and words
        lines = text.count('\n') + 1
        words = len(text.split())
        
        metadata = {
            "title": original_filename,
            "line_count": lines,
            "word_count": words,
            "file_type": "TXT"
        }
        
        return text, metadata
    
    def _extract_from_docx(self, file_path: str, original_filename: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text and metadata from a DOCX file.
        
        Args:
            file_path: Path to the DOCX file.
            original_filename: Original name of the uploaded file.
            
        Returns:
            Tuple of extracted text and metadata.
        """
        # This is a placeholder. In a real implementation, you'd use a library like python-docx
        # For now, we'll raise an error
        raise NotImplementedError("DOCX extraction not yet implemented")
    
    def _chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into chunks for vectorization.
        
        Args:
            text: The text to chunk.
            metadata: Document metadata to attach to each chunk.
            
        Returns:
            List of chunks with metadata.
        """
        # Use LangChain's text splitter for intelligent chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Split the text
        text_chunks = text_splitter.split_text(text)
        
        # Create chunks with metadata
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            # Try to identify page number from chunk text
            page_num = None
            page_markers = [line for line in chunk_text.split('\n') if "--- Page " in line]
            if page_markers:
                for marker in page_markers:
                    try:
                        page_num = int(marker.replace("--- Page ", "").replace(" ---", ""))
                        break
                    except ValueError:
                        continue
            
            # Create chunk with metadata
            chunk = {
                "content": chunk_text,
                "metadata": {
                    "chunk_id": i,
                    "source": metadata.get("title", "Unknown"),
                    "page": page_num,
                    "document_type": metadata.get("file_type", "Unknown")
                }
            }
            chunks.append(chunk)
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def _store_chunks(self, document_id: str, chunks: List[Dict[str, Any]], metadata: Dict[str, Any]) -> None:
        """
        Store chunks in the vector database.
        
        Args:
            document_id: ID of the document.
            chunks: List of text chunks with metadata.
            metadata: Document metadata.
        """
        # Add document_id to each chunk's metadata
        for chunk in chunks:
            chunk["metadata"]["document_id"] = document_id
        
        # Store in vector database
        self.vector_store.add_texts(
            document_id=document_id,
            chunks=chunks,
            metadata=metadata
        )
        
        logger.info(f"Stored {len(chunks)} chunks in vector database for document {document_id}")

# Test function
def test_document_processor():
    """Test the document processor with a sample PDF."""
    processor = DocumentProcessor()
    
    # Create a simple test PDF
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
        temp.write(b"This is a test document.\nIt has multiple lines.\n\nAnd multiple paragraphs.")
        temp_path = temp.name
    
    try:
        # Process the document
        document_id, metadata = processor.process_document(temp_path, "test_document.txt")
        
        print("\n--- Test Results ---")
        print(f"Document ID: {document_id}")
        print(f"Metadata: {metadata}")
        print("-------------------\n")
        
        # Clean up
        os.unlink(temp_path)
        
        return True
    except Exception as e:
        logger.error(f"Test failed: {e}")
        
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        return False

if __name__ == "__main__":
    test_document_processor()
