"""
Citation extraction service for Health AI Consultant.
Extracts citations from model responses and calculates confidence scores.
"""
import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CitationExtractor:
    """Service for extracting citations from model responses."""
    
    @staticmethod
    def extract_citations(response: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract citations from a model response.
        
        Args:
            response: The model's response text.
            context_chunks: The context chunks used to generate the response.
            
        Returns:
            Dictionary with citations and confidence score.
        """
        # Initialize result structure
        result = {
            "citations": [],
            "confidence_score": 0.0
        }
        
        if not response or not context_chunks:
            return result
        
        # First try to extract explicit citations in [Source: X] format
        explicit_citations = CitationExtractor._extract_explicit_citations(response, context_chunks)
        
        # If explicit citations found, use them
        if explicit_citations["citations"]:
            return explicit_citations
        
        # Otherwise, try to match content with context chunks
        return CitationExtractor._extract_implicit_citations(response, context_chunks)
    
    @staticmethod
    def _extract_explicit_citations(response: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract explicit citations in [Source: X] format.
        
        Args:
            response: The model's response text.
            context_chunks: The context chunks used to generate the response.
            
        Returns:
            Dictionary with citations and confidence score.
        """
        citations = []
        source_pattern = r'\[Source:?\s*([^\]]+)\]'
        
        # Find all source mentions
        source_matches = re.finditer(source_pattern, response)
        
        # Create a mapping of titles/sources to context chunk indices
        source_map = {}
        for i, chunk in enumerate(context_chunks):
            metadata = chunk.get('metadata', {})
            title = metadata.get('title', '').lower()
            source = metadata.get('source', '').lower()
            
            if title:
                source_map[title] = i
            if source:
                source_map[source] = i
        
        # Process each source mention
        for match in source_matches:
            source_text = match.group(1).strip()
            
            # Find the sentence or paragraph containing this citation
            start_pos = max(0, match.start() - 200)  # Look back up to 200 chars
            end_pos = min(len(response), match.end() + 50)  # Look ahead up to 50 chars
            
            # Extract the surrounding text
            surrounding_text = response[start_pos:end_pos]
            
            # Find the sentence ending before the citation
            sentence_end_pos = match.start() - start_pos
            sentence_start_pos = max(0, surrounding_text.rfind('.', 0, sentence_end_pos) + 1)
            
            if sentence_start_pos >= sentence_end_pos:
                sentence_start_pos = max(0, surrounding_text.rfind('\n', 0, sentence_end_pos) + 1)
            
            # Extract the cited text
            cited_text = surrounding_text[sentence_start_pos:sentence_end_pos].strip()
            
            # Find matching context chunk
            source_index = None
            source_text_lower = source_text.lower()
            
            # Try exact match first
            if source_text_lower in source_map:
                source_index = source_map[source_text_lower]
            else:
                # Try partial match
                for key, idx in source_map.items():
                    if key in source_text_lower or source_text_lower in key:
                        source_index = idx
                        break
            
            # If we found a matching source, add the citation
            if source_index is not None and cited_text:
                citations.append({
                    "text": cited_text,
                    "source_index": source_index
                })
        
        # Calculate confidence score based on number of citations
        confidence_score = min(1.0, len(citations) / max(1, len(context_chunks)))
        
        return {
            "citations": citations,
            "confidence_score": confidence_score
        }
    
    @staticmethod
    def _extract_implicit_citations(response: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract implicit citations by matching response content with context chunks.
        
        Args:
            response: The model's response text.
            context_chunks: The context chunks used to generate the response.
            
        Returns:
            Dictionary with citations and confidence score.
        """
        citations = []
        total_matched_chars = 0
        
        # Split response into sentences
        sentences = re.split(r'(?<=[.!?])\s+', response)
        
        # For each sentence, try to find matching content in context chunks
        for sentence in sentences:
            if len(sentence.strip()) < 10:  # Skip very short sentences
                continue
                
            best_match = None
            best_match_score = 0
            best_chunk_idx = -1
            
            # Compare with each context chunk
            for i, chunk in enumerate(context_chunks):
                content = chunk.get('content', '')
                
                # Calculate simple matching score (can be improved with more sophisticated algorithms)
                match_score = CitationExtractor._calculate_match_score(sentence, content)
                
                if match_score > best_match_score and match_score > 0.3:  # Threshold for considering a match
                    best_match = sentence
                    best_match_score = match_score
                    best_chunk_idx = i
            
            # If we found a good match, add it as a citation
            if best_match and best_chunk_idx >= 0:
                # Check if this sentence overlaps significantly with any existing citation
                is_new = True
                for citation in citations:
                    if CitationExtractor._calculate_match_score(best_match, citation["text"]) > 0.5:
                        is_new = False
                        break
                
                if is_new:
                    citations.append({
                        "text": best_match,
                        "source_index": best_chunk_idx
                    })
                    total_matched_chars += len(best_match)
        
        # Calculate confidence score based on proportion of response that was matched
        response_length = len(response.strip())
        confidence_score = min(1.0, total_matched_chars / max(1, response_length))
        
        return {
            "citations": citations,
            "confidence_score": confidence_score
        }
    
    @staticmethod
    def _calculate_match_score(text1: str, text2: str) -> float:
        """
        Calculate a simple matching score between two texts.
        
        Args:
            text1: First text string.
            text2: Second text string.
            
        Returns:
            Matching score between 0 and 1.
        """
        # Convert to lowercase for comparison
        text1 = text1.lower()
        text2 = text2.lower()
        
        # Check for direct containment
        if text1 in text2:
            return len(text1) / len(text2)
        if text2 in text1:
            return len(text2) / len(text1)
        
        # Count matching words
        words1 = set(re.findall(r'\b\w+\b', text1))
        words2 = set(re.findall(r'\b\w+\b', text2))
        
        if not words1 or not words2:
            return 0
        
        common_words = words1.intersection(words2)
        
        # Calculate Jaccard similarity
        return len(common_words) / len(words1.union(words2))

# Test function
def test_citation_extractor():
    """Test the citation extractor with sample data."""
    # Sample context chunks
    context_chunks = [
        {
            'content': 'Regular exercise has been shown to reduce the risk of heart disease by up to 30%.',
            'metadata': {
                'title': 'Cardiovascular Health Guidelines',
                'source': 'American Heart Association',
                'page': 42
            }
        },
        {
            'content': 'A diet rich in fruits, vegetables, and whole grains can help maintain healthy cholesterol levels.',
            'metadata': {
                'title': 'Nutrition and Heart Health',
                'source': 'Journal of Nutrition',
                'page': 118
            }
        }
    ]
    
    # Test explicit citations
    response_with_explicit = (
        "To improve heart health, you should exercise regularly, which can reduce heart disease risk "
        "by up to 30% [Source: American Heart Association]. Additionally, eating a diet rich in fruits, "
        "vegetables, and whole grains helps maintain healthy cholesterol levels [Source: Journal of Nutrition]."
    )
    
    explicit_result = CitationExtractor.extract_citations(response_with_explicit, context_chunks)
    print("\n--- Explicit Citations Result ---")
    print(json.dumps(explicit_result, indent=2))
    print("--------------------------------\n")
    
    # Test implicit citations
    response_with_implicit = (
        "To improve heart health, you should exercise regularly, which can reduce heart disease risk "
        "by up to 30%. Additionally, eating a diet rich in fruits, vegetables, and whole grains helps "
        "maintain healthy cholesterol levels."
    )
    
    implicit_result = CitationExtractor.extract_citations(response_with_implicit, context_chunks)
    print("\n--- Implicit Citations Result ---")
    print(json.dumps(implicit_result, indent=2))
    print("--------------------------------\n")
    
    return True

if __name__ == "__main__":
    test_citation_extractor()
