"""
Query preprocessing service for Health AI Consultant.
Provides utilities for cleaning, validating, and enhancing user queries.
"""
import re
import logging
import string
from typing import Dict, Any, Tuple, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QueryProcessor:
    """Service for preprocessing user queries before retrieval and inference."""
    
    def __init__(self, 
                 min_query_length: int = 3,
                 max_query_length: int = 500,
                 remove_special_chars: bool = True,
                 normalize_whitespace: bool = True):
        """
        Initialize the query processor.
        
        Args:
            min_query_length: Minimum acceptable query length.
            max_query_length: Maximum acceptable query length.
            remove_special_chars: Whether to remove special characters.
            normalize_whitespace: Whether to normalize whitespace.
        """
        self.min_query_length = min_query_length
        self.max_query_length = max_query_length
        self.remove_special_chars = remove_special_chars
        self.normalize_whitespace = normalize_whitespace
        
        # Common health-related stopwords to keep (don't remove these)
        self.health_terms = {
            'covid', 'diabetes', 'cancer', 'heart', 'disease', 'virus', 'bacteria',
            'infection', 'symptom', 'diagnosis', 'treatment', 'medicine', 'drug',
            'vaccine', 'prescription', 'dose', 'therapy', 'surgery', 'blood',
            'pressure', 'cholesterol', 'diet', 'exercise', 'nutrition', 'vitamin',
            'protein', 'carbohydrate', 'fat', 'mineral', 'immune', 'allergy',
            'chronic', 'acute', 'pain', 'inflammation', 'fever', 'cough', 'headache'
        }
        
        logger.info("Query processor initialized")
    
    def preprocess_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Preprocess a user query.
        
        Args:
            query: The raw user query.
            
        Returns:
            Tuple containing:
                - The processed query.
                - A dictionary of metadata about the processing.
        """
        if not query or not isinstance(query, str):
            return "", {"valid": False, "error": "Query must be a non-empty string"}
        
        original_query = query
        metadata = {
            "original_length": len(query),
            "changes": [],
            "valid": True,
            "error": None
        }
        
        # Trim whitespace
        query = query.strip()
        if query != original_query:
            metadata["changes"].append("trimmed_whitespace")
        
        # Check minimum length
        if len(query) < self.min_query_length:
            metadata["valid"] = False
            metadata["error"] = f"Query is too short (minimum {self.min_query_length} characters)"
            return query, metadata
        
        # Check maximum length
        if len(query) > self.max_query_length:
            query = query[:self.max_query_length]
            metadata["changes"].append("truncated")
        
        # Normalize whitespace
        if self.normalize_whitespace:
            original = query
            query = re.sub(r'\s+', ' ', query)
            if query != original:
                metadata["changes"].append("normalized_whitespace")
        
        # Remove special characters (but keep health-related terms)
        if self.remove_special_chars:
            original = query
            # Only remove certain special characters, keeping those that might be important
            # like hyphens in medical terms, percentages, etc.
            query = re.sub(r'[^\w\s\-\%\+\.\/]', ' ', query)
            query = re.sub(r'\s+', ' ', query).strip()
            if query != original:
                metadata["changes"].append("removed_special_chars")
        
        # Add metadata about the final query
        metadata["processed_length"] = len(query)
        metadata["processing_ratio"] = len(query) / metadata["original_length"] if metadata["original_length"] > 0 else 0
        
        return query, metadata
    
    def extract_health_entities(self, query: str) -> List[str]:
        """
        Extract potential health-related entities from the query.
        
        Args:
            query: The user query.
            
        Returns:
            List of potential health entities.
        """
        # Simple extraction based on our health terms list
        # In a production system, this could use NER or a medical entity extractor
        words = re.findall(r'\b\w+\b', query.lower())
        entities = [word for word in words if word in self.health_terms]
        
        return entities
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a query is acceptable.
        
        Args:
            query: The query to validate.
            
        Returns:
            Tuple containing:
                - Boolean indicating if the query is valid.
                - Error message if invalid, None otherwise.
        """
        # Check if query is empty or just whitespace
        if not query or query.isspace():
            return False, "Query cannot be empty"
        
        # Check minimum length
        if len(query) < self.min_query_length:
            return False, f"Query is too short (minimum {self.min_query_length} characters)"
        
        # Check maximum length
        if len(query) > self.max_query_length:
            return False, f"Query is too long (maximum {self.max_query_length} characters)"
        
        # Check if query is just punctuation
        if all(c in string.punctuation for c in query if not c.isspace()):
            return False, "Query cannot consist only of punctuation"
        
        # Check for potentially harmful content (basic check)
        harmful_patterns = [
            r'(?i)(?:drop|delete|truncate|alter)\s+(?:table|database)',
            r'(?i)(?:insert|update)\s+into',
            r'(?i)(?:select|union).+(?:from)',
            r'(?i)(?:exec|execute|eval)',
            r'(?i)(?:system|os|subprocess)'
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, query):
                return False, "Query contains potentially harmful content"
        
        return True, None


# Test function
def test_query_processor():
    """Test the query processor with sample queries."""
    processor = QueryProcessor()
    
    test_queries = [
        "What are the symptoms of COVID-19?",
        "   Too much whitespace   around   this    query   ",
        "Short",
        "This query has some special characters like @#$%^&*()!",
        "What's the recommended dosage of ibuprofen for adults?",
        "SELECT * FROM users; DROP TABLE users;",  # Potentially harmful
        "A" * 600  # Too long
    ]
    
    print("\n--- Query Processor Test Results ---")
    for i, query in enumerate(test_queries):
        processed, metadata = processor.preprocess_query(query)
        valid, error = processor.validate_query(query)
        
        print(f"\nTest {i+1}:")
        print(f"Original: '{query}'")
        print(f"Processed: '{processed}'")
        print(f"Valid: {valid}")
        if error:
            print(f"Error: {error}")
        print(f"Metadata: {metadata}")
        
        if metadata["changes"]:
            print(f"Changes: {', '.join(metadata['changes'])}")
        
        entities = processor.extract_health_entities(query)
        if entities:
            print(f"Health entities: {', '.join(entities)}")
    
    return True


if __name__ == "__main__":
    # Test the query processor when run directly
    test_query_processor()
