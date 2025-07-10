"""
Vector store service for Health AI Consultant.
Provides utilities for interacting with the ChromaDB vector database.
"""
import os
import sys
import logging
from typing import List, Dict, Any, Optional, Union
import chromadb
from chromadb.utils import embedding_functions

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorStoreService:
    """Service for interacting with the ChromaDB vector database."""
    
    def __init__(self, 
                 db_path: str = config.VECTOR_DB_PATH,
                 embedding_model: str = config.OLLAMA_EMBEDDING_MODEL,
                 collection_name: str = "health_documents"):
        """
        Initialize the vector store service.
        
        Args:
            db_path: Path to the ChromaDB database.
            embedding_model: Name of the Ollama embedding model to use.
            collection_name: Name of the collection to use.
        """
        self.db_path = db_path
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        
        # Create a custom embedding function that works with Ollama
        self.embedding_function = self._create_custom_ollama_embedding_function(
            model_name=embedding_model,
            url=config.OLLAMA_BASE_URL
        )
        
        # Initialize the client and collection
        self._init_client()
        
        logger.info(f"Initialized vector store service with collection: {collection_name}")
    
    def _create_custom_ollama_embedding_function(self, model_name, url):
        """Create a custom embedding function that works with Ollama API.
        
        Args:
            model_name: Name of the Ollama model to use for embeddings.
            url: Base URL of the Ollama API.
            
        Returns:
            A class that implements the ChromaDB EmbeddingFunction interface.
        """
        import httpx
        import json
        import numpy as np
        from chromadb.api.types import Documents, EmbeddingFunction
        
        # Define a class that implements the ChromaDB EmbeddingFunction interface
        class CustomOllamaEmbedding(EmbeddingFunction):
            def __init__(self, model_name, url):
                self.model_name = model_name
                self.url = url
            
            def __call__(self, input: Documents) -> list:
                """Generate embeddings for the input texts.
                
                Args:
                    input: List of texts to generate embeddings for.
                    
                Returns:
                    List of embeddings, one for each input text.
                """
                # Generate embeddings for each text
                embeddings = []
                for text in input:
                    try:
                        # Make a request to the Ollama API
                        response = httpx.post(
                            f"{url}/api/embeddings",
                            json={"model": model_name, "prompt": text}
                        )
                        response.raise_for_status()
                        
                        # Parse the response
                        data = response.json()
                        embedding = data.get('embedding')
                        
                        if embedding:
                            embeddings.append(embedding)
                        else:
                            logger.error(f"No embedding returned for text: {text[:50]}...")
                            # Return a zero vector as fallback
                            embeddings.append([0.0] * 768)  # Typical embedding size
                    except Exception as e:
                        logger.error(f"Error generating embedding: {e}")
                        # Return a zero vector as fallback
                        embeddings.append([0.0] * 768)  # Typical embedding size
                
                return embeddings
        
        return CustomOllamaEmbedding(model_name, url)

    def _init_client(self):
        """Initialize the ChromaDB client and collection."""
        try:
            # Create the database directory if it doesn't exist
            os.makedirs(self.db_path, exist_ok=True)
            
            # Initialize the persistent client
            self.client = chromadb.PersistentClient(path=self.db_path)
            
            # Get or create the collection
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Connected to existing collection: {self.collection_name}")
            except Exception:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Created new collection: {self.collection_name}")
        
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {e}")
            raise
    
    def add_documents(self, 
                     texts: List[str], 
                     metadatas: List[Dict[str, Any]], 
                     ids: Optional[List[str]] = None) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of document texts.
            metadatas: List of metadata dictionaries for each document.
            ids: Optional list of IDs for each document. If not provided, UUIDs will be generated.
            
        Returns:
            List of document IDs.
        """
        try:
            # Generate UUIDs if IDs are not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in range(len(texts))]
            
            # Add documents to the collection
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} documents to collection: {self.collection_name}")
            return ids
        
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def search(self, 
              query: str, 
              n_results: int = 5, 
              where: Optional[Dict[str, Any]] = None,
              include_metadata: bool = True) -> Dict[str, Any]:
        """
        Search for similar documents in the vector store.
        
        Args:
            query: The query text.
            n_results: Number of results to return.
            where: Optional filter to apply to the search.
            include_metadata: Whether to include metadata in the results.
            
        Returns:
            Dictionary containing search results.
        """
        try:
            # Prepare include list based on what to include in results
            include_list = ["documents", "distances"]
            if include_metadata:
                include_list.append("metadatas")
                
            # Perform the query
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where,
                include=include_list
            )
            
            logger.info(f"Searched for: '{query}', found {len(results['documents'][0])} results")
            return results
        
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def get_relevant_context(self, 
                           query: str, 
                           n_results: int = 5, 
                           where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get relevant context for a query.
        
        Args:
            query: The query text.
            n_results: Number of results to return.
            where: Optional filter to apply to the search.
            
        Returns:
            List of dictionaries containing document text and metadata.
        """
        try:
            # Search for relevant documents
            results = self.search(query, n_results, where)
            
            # Format the results
            context = []
            for i in range(len(results["documents"][0])):
                # Extract metadata or create empty dict if none exists
                metadata = results["metadatas"][0][i] if "metadatas" in results and results["metadatas"] else {}
                
                # Create citation information
                citation = self._format_citation(metadata)
                
                # Calculate confidence score (inverse of distance - closer is better)
                distance = results["distances"][0][i] if "distances" in results else 1.0
                confidence_score = 1.0 - min(distance, 1.0)  # Normalize to 0-1 range, higher is better
                
                context.append({
                    "text": results["documents"][0][i],
                    "metadata": metadata,
                    "id": results["ids"][0][i] if "ids" in results else f"doc_{i}",
                    "score": distance,  # Original distance score (lower is better)
                    "confidence": round(confidence_score, 2),  # Confidence score (higher is better)
                    "citation": citation
                })
            
            # Sort by confidence (highest first)
            context.sort(key=lambda x: x["confidence"], reverse=True)
            
            return context
        
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            raise
    
    def _format_citation(self, metadata: Dict[str, Any]) -> str:
        """
        Format metadata into a citation string.
        
        Args:
            metadata: The metadata dictionary.
            
        Returns:
            A formatted citation string.
        """
        # Extract common citation fields from metadata
        source = metadata.get("source", "Unknown Source")
        page = metadata.get("page", None)
        title = metadata.get("title", None)
        author = metadata.get("author", None)
        date = metadata.get("date", None)
        url = metadata.get("url", None)
        topic = metadata.get("topic", None)
        
        # Build citation parts
        citation_parts = []
        
        # Add title or source
        if title:
            citation_parts.append(f"\"{title}\"")
        else:
            citation_parts.append(source)
        
        # Add author if available
        if author:
            citation_parts.append(f"by {author}")
        
        # Add date if available
        if date:
            citation_parts.append(f"({date})")
        
        # Add page if available
        if page:
            citation_parts.append(f"p. {page}")
        
        # Add topic if available and not already in title
        if topic and (not title or topic.lower() not in title.lower()):
            citation_parts.append(f"Topic: {topic}")
        
        # Add URL if available
        if url:
            citation_parts.append(f"URL: {url}")
        
        # Join all parts with appropriate separators
        citation = ", ".join(citation_parts)
        
        return citation
    
    def delete_collection(self):
        """Delete the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise
    
    def add_texts(self, document_id: str, chunks: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
        """
        Add text chunks from a document to the vector store.
        
        Args:
            document_id: ID of the document.
            chunks: List of dictionaries containing text content and metadata.
            metadata: Document-level metadata.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Extract texts and metadatas from chunks
            texts = [chunk["content"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            # Generate IDs for each chunk
            ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            
            # Add to vector store
            self.add_documents(texts, metadatas, ids)
            
            # Store document metadata in a separate collection or database
            # For now, we'll add a special entry in the vector store
            self.collection.add(
                documents=[f"Document metadata for {document_id}"],
                metadatas=[{"document_id": document_id, "is_metadata": True, **metadata}],
                ids=[f"{document_id}_metadata"]
            )
            
            return True
        except Exception as e:
            logger.error(f"Error adding text chunks to vector store: {e}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the vector store.
        
        Returns:
            List of document metadata.
        """
        try:
            # Query for all items with is_metadata=True
            results = self.collection.get(
                where={"is_metadata": True}
            )
            
            # Extract and format document metadata
            documents = []
            if results and results["metadatas"]:
                for i, metadata in enumerate(results["metadatas"]):
                    # Remove internal flags
                    doc_metadata = {k: v for k, v in metadata.items() if k != "is_metadata"}
                    documents.append(doc_metadata)
            
            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific document.
        
        Args:
            document_id: ID of the document to retrieve.
            
        Returns:
            Document metadata or None if not found.
        """
        try:
            # Query for the document metadata
            results = self.collection.get(
                ids=[f"{document_id}_metadata"]
            )
            
            # Extract and return metadata if found
            if results and results["metadatas"] and len(results["metadatas"]) > 0:
                metadata = results["metadatas"][0]
                # Remove internal flags
                return {k: v for k, v in metadata.items() if k != "is_metadata"}
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting document metadata: {e}")
            return None
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its chunks from the vector store.
        
        Args:
            document_id: ID of the document to delete.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            # Delete all chunks and metadata
            if results and results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"Deleted document {document_id} with {len(results['ids'])} chunks")
                return True
            else:
                logger.warning(f"Document {document_id} not found")
                return False
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False


# Test function
def test_vector_store():
    """Test the vector store service with sample documents."""
    service = VectorStoreService()
    
    try:
        # Check if the collection is empty
        try:
            count = service.collection.count()
            if count == 0:
                # Add sample documents for testing
                texts = [
                    "Regular exercise can help improve cardiovascular health and reduce the risk of heart disease.",
                    "A balanced diet rich in fruits and vegetables provides essential nutrients for overall health.",
                    "Adequate sleep is crucial for mental health and cognitive function.",
                    "Stress management techniques like meditation can help reduce anxiety and improve well-being.",
                    "Regular health check-ups can help detect potential health issues early."
                ]
                
                metadatas = [
                    {"source": "Health Guidelines", "topic": "exercise", "page": 1},
                    {"source": "Nutrition Handbook", "topic": "diet", "page": 15},
                    {"source": "Sleep Research Journal", "topic": "sleep", "page": 7},
                    {"source": "Mental Health Resources", "topic": "stress", "page": 22},
                    {"source": "Preventive Care Guide", "topic": "check-ups", "page": 3}
                ]
                
                service.add_documents(texts, metadatas)
                print("[INFO] Added sample documents to the vector store.")
            else:
                print(f"[INFO] Collection already contains {count} documents.")
        except Exception as e:
            logger.error(f"Error checking collection: {e}")
        
        # Test search functionality
        query = "What are the benefits of regular exercise?"
        results = service.get_relevant_context(query, n_results=2)
        
        print("\n--- Test Search Results ---")
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"Text: {result['text']}")
            print(f"Source: {result['metadata'].get('source', 'Unknown')}")
            print(f"Topic: {result['metadata'].get('topic', 'Unknown')}")
            print(f"Score: {result['score']}")
            print()
        
        return True
    
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the vector store service when run directly
    success = test_vector_store()
    
    if success:
        print("[SUCCESS] Vector store service is working correctly!")
        sys.exit(0)
    else:
        print("[FAILED] Vector store service test failed!")
        sys.exit(1)
