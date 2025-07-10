"""
Prompt templates for Health AI Consultant.
Provides structured templates for different types of prompts.
"""
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PromptTemplates:
    """Collection of prompt templates for the Health AI Consultant."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """
        Get the default system prompt for health consultations.
        
        Returns:
            The default system prompt.
        """
        return (
            "You are a helpful AI health consultant. Your role is to provide informative, "
            "evidence-based health information. Remember to:\n"
            "1. Be accurate and cite your sources when possible.\n"
            "2. Acknowledge limitations in your knowledge.\n"
            "3. Never provide medical diagnoses or prescribe treatments.\n"
            "4. Recommend consulting healthcare professionals for specific medical concerns.\n"
            "5. Focus on general health education and information.\n"
            "6. Be empathetic and supportive while maintaining professionalism.\n"
            "7. Only provide information that is supported by the given context.\n"
            "8. If you don't know or the information isn't in the context, say so clearly.\n"
            "9. When citing sources, use the format [Source: Title]."
        )
    
    @staticmethod
    def format_rag_prompt(question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Format a RAG prompt with retrieved context chunks.
        
        Args:
            question: The user's question.
            context_chunks: List of context chunks with metadata.
            
        Returns:
            Formatted prompt with context.
        """
        if not context_chunks:
            return f"Question: {question}\n\nAnswer:"
        
        # Format each context chunk with its metadata
        formatted_contexts = []
        for i, chunk in enumerate(context_chunks):
            # Extract content and metadata
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})
            
            # Format source information
            source_info = []
            if 'title' in metadata:
                source_info.append(f"Title: {metadata['title']}")
            if 'source' in metadata:
                source_info.append(f"Source: {metadata['source']}")
            if 'page' in metadata:
                source_info.append(f"Page: {metadata['page']}")
            
            # Combine source info
            source_str = " | ".join(source_info) if source_info else "Unknown source"
            
            # Format the context with metadata
            formatted_context = (
                f"[Context {i+1}]\n"
                f"{content}\n"
                f"[Source: {source_str}]\n"
            )
            formatted_contexts.append(formatted_context)
        
        # Join all formatted contexts
        all_contexts = "\n".join(formatted_contexts)
        
        # Construct the full prompt
        full_prompt = (
            f"Please answer the following question based on the provided context information. "
            f"If the context doesn't contain relevant information, acknowledge that you don't have "
            f"enough information to provide a complete answer.\n\n"
            f"--- CONTEXT INFORMATION ---\n"
            f"{all_contexts}\n"
            f"--- END OF CONTEXT ---\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        
        return full_prompt
    
    @staticmethod
    def format_citation_prompt(model_response: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Format a prompt to extract citations from a model response.
        
        Args:
            model_response: The model's response to the query.
            context_chunks: The context chunks used to generate the response.
            
        Returns:
            Prompt for citation extraction.
        """
        # Format context sources
        sources = []
        for i, chunk in enumerate(context_chunks):
            metadata = chunk.get('metadata', {})
            title = metadata.get('title', f"Source {i+1}")
            source = metadata.get('source', 'Unknown')
            sources.append(f"{i+1}. {title} ({source})")
        
        sources_text = "\n".join(sources)
        
        prompt = (
            f"Below is a health-related response and a list of sources that were used to create it.\n\n"
            f"Response:\n{model_response}\n\n"
            f"Sources:\n{sources_text}\n\n"
            f"Please identify which sources were actually used in the response and provide a JSON object "
            f"with citations in the following format:\n"
            f"{{\n"
            f"  \"citations\": [\n"
            f"    {{\n"
            f"      \"text\": \"<text from the response that uses this source>\",\n"
            f"      \"source_index\": <index number of the source>\n"
            f"    }},\n"
            f"    ...\n"
            f"  ],\n"
            f"  \"confidence_score\": <number between 0 and 1 indicating how well the response is supported by the sources>\n"
            f"}}\n\n"
            f"Only include citations for information that clearly comes from the sources. "
            f"If no sources were used, return an empty citations array and a confidence score of 0."
        )
        
        return prompt

# Test function
def test_prompt_templates():
    """Test the prompt templates with sample data."""
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
    
    # Test RAG prompt
    question = "What are some ways to improve heart health?"
    rag_prompt = PromptTemplates.format_rag_prompt(question, context_chunks)
    print("\n--- RAG Prompt ---")
    print(rag_prompt)
    print("------------------\n")
    
    # Test citation prompt
    model_response = (
        "To improve heart health, you should exercise regularly, which can reduce heart disease risk by up to 30%. "
        "Additionally, eating a diet rich in fruits, vegetables, and whole grains helps maintain healthy cholesterol levels."
    )
    citation_prompt = PromptTemplates.format_citation_prompt(model_response, context_chunks)
    print("\n--- Citation Prompt ---")
    print(citation_prompt)
    print("------------------------\n")
    
    return True

if __name__ == "__main__":
    test_prompt_templates()
