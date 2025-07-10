"""
Chat API endpoint for Health AI Consultant.
Provides the main chat functionality with RAG-powered responses.
"""
import logging
from flask import Blueprint, request, jsonify
from services.vector_store import VectorStoreService
from services.ollama_client import OllamaClient
from services.query_processor import QueryProcessor
from services.inference import InferenceService
from services.prompt_templates import PromptTemplates
from services.citation_extractor import CitationExtractor
from api.error_handlers import handle_invalid_request, handle_ollama_error, handle_vector_db_error, handle_internal_server_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api')

# Initialize services
vector_store = VectorStoreService()
query_processor = QueryProcessor()
inference_service = InferenceService()

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Process a chat request with RAG.
    
    Request body:
    {
        "question": "User's health-related question",
        "context": "Optional previous conversation context",
        "max_tokens": 500,  # Optional
        "temperature": 0.7,  # Optional
        "stream": false      # Optional
    }
    
    Returns:
    {
        "answer": "Generated response",
        "citations": [
            {
                "text": "Cited text",
                "source": "Source document",
                "confidence": 0.95
            }
        ],
        "confidence_score": 0.85
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return handle_invalid_request("Request must be JSON")
        
        data = request.get_json()
        
        # Validate required fields
        if 'question' not in data or not data['question']:
            return handle_invalid_request("Question is required")
        
        # Get parameters
        question = data['question']
        context = data.get('context', '')
        max_tokens = data.get('max_tokens', 500)
        temperature = data.get('temperature', 0.7)
        stream = data.get('stream', False)
        
        # Process the query
        try:
            processed_question, metadata = query_processor.preprocess_query(question)
            
            # Check if query is valid
            if not metadata['valid']:
                return handle_invalid_request(metadata['error'])
            
            # Log the processed query
            logger.info(f"Processing query: '{processed_question}'")
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return handle_invalid_request(f"Error processing query: {str(e)}")
        
        # Retrieve relevant context
        try:
            retrieval_results = vector_store.get_relevant_context(processed_question, n_results=5)
            logger.info(f"Retrieved {len(retrieval_results)} context items")
            
            # Convert retrieval results to the format expected by PromptTemplates
            context_chunks = []
            for result in retrieval_results:
                chunk = {
                    'content': result.get('text', ''),
                    'metadata': {
                        'title': result.get('title', 'Unknown'),
                        'source': result.get('source', 'Unknown'),
                        'page': result.get('page', None),
                        'similarity_score': result.get('score', 0.0)
                    }
                }
                context_chunks.append(chunk)
                
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return handle_vector_db_error(e)
        
        # Format prompt with context using our template service
        prompt = PromptTemplates.format_rag_prompt(processed_question, context_chunks)
        system_prompt = PromptTemplates.get_system_prompt()
        
        # Generate response using inference service
        try:
            # Get response from Ollama
            response = inference_service.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract the generated text
            answer = response.get('response', '')
            
            # Extract citations using our citation extractor
            citation_data = CitationExtractor.extract_citations(answer, context_chunks)
            
            # Format citations for the API response
            formatted_citations = []
            for citation in citation_data['citations']:
                # Get the source chunk
                source_index = citation.get('source_index', 0)
                if 0 <= source_index < len(context_chunks):
                    chunk = context_chunks[source_index]
                    metadata = chunk.get('metadata', {})
                    
                    formatted_citations.append({
                        "text": citation.get('text', ''),
                        "source": {
                            "title": metadata.get('title', 'Unknown'),
                            "source": metadata.get('source', 'Unknown'),
                            "page": metadata.get('page')
                        },
                        "similarity_score": metadata.get('similarity_score', 0.0)
                    })
            
            # Calculate confidence score
            confidence_score = citation_data.get('confidence_score', 0.0)
            
            # Enhance confidence score with retrieval similarity scores
            if formatted_citations:
                # Average of citation similarity scores and extraction confidence
                similarity_scores = [c.get('similarity_score', 0.0) for c in formatted_citations]
                avg_similarity = sum(similarity_scores) / len(similarity_scores)
                # Weight the confidence score (70% extraction confidence, 30% similarity)
                confidence_score = (0.7 * confidence_score) + (0.3 * avg_similarity)
            
            # Return the response with citations and confidence score
            return jsonify({
                "answer": answer,
                "citations": formatted_citations,
                "confidence_score": confidence_score,
                "model": response.get('model', 'unknown')
            })
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return handle_ollama_error(e)
    
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@chat_bp.route('/chat/stream', methods=['POST'])
def chat_stream():
    """
    Process a chat request with RAG and stream the response.
    
    This endpoint is similar to /chat but streams the response back to the client.
    """
    # This is a placeholder for streaming functionality
    # We'll implement this in a future iteration
    return jsonify({"error": "Streaming not yet implemented"}), 501
