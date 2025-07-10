"""
Inference service for Health AI Consultant.
Provides utilities for generating responses from Ollama models.
"""
import os
import sys
import logging
from typing import Dict, Any, List, Optional, Generator, Union

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from services.ollama_client import OllamaClient
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InferenceService:
    """Service for generating responses from Ollama models."""
    
    def __init__(self, 
                 base_url: str = config.OLLAMA_BASE_URL,
                 model: str = config.OLLAMA_MODEL):
        """
        Initialize the inference service.
        
        Args:
            base_url: Base URL for the Ollama API.
            model: Default model to use for inference.
        """
        self.client = OllamaClient(base_url)
        self.model = model
        logger.info(f"Initialized inference service with model: {model}")
    
    def generate_response(self, 
                         prompt: str, 
                         context: Optional[List[str]] = None,
                         system_prompt: Optional[str] = None,
                         stream: bool = False,
                         **kwargs) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Generate a response from the model.
        
        Args:
            prompt: The user's question or prompt.
            context: Optional list of context strings to include in the prompt.
            system_prompt: Optional system prompt to guide the model's behavior.
            stream: Whether to stream the response.
            **kwargs: Additional parameters to pass to the Ollama API.
            
        Returns:
            Dictionary containing the response or a generator yielding response chunks.
        """
        # Prepare the full prompt with context if provided
        full_prompt = self._prepare_prompt(prompt, context)
        
        # Use the default system prompt if none is provided
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        
        try:
            return self.client.generate(
                prompt=full_prompt,
                model=self.model,
                system=system_prompt,
                stream=stream,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def _prepare_prompt(self, prompt: str, context: Optional[List[str]] = None) -> str:
        """
        Prepare the full prompt with context.
        
        Args:
            prompt: The user's question or prompt.
            context: Optional list of context strings to include in the prompt.
            
        Returns:
            The full prompt with context.
        """
        if not context:
            return prompt
        
        # Join context chunks with separators
        context_text = "\n\n".join([f"Context {i+1}:\n{chunk}" for i, chunk in enumerate(context)])
        
        # Construct the full prompt
        full_prompt = (
            f"Based on the following context, please answer the question.\n\n"
            f"{context_text}\n\n"
            f"Question: {prompt}\n\n"
            f"Answer:"
        )
        
        return full_prompt
    
    def _get_default_system_prompt(self) -> str:
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
            "8. If you don't know or the information isn't in the context, say so clearly."
        )


# Test function
def test_inference_service():
    """Test the inference service with a simple query."""
    service = InferenceService()
    
    try:
        # Test with a simple health question
        response = service.generate_response(
            prompt="What are some ways to improve cardiovascular health?",
            temperature=0.7,
            max_tokens=500
        )
        
        print("\n--- Test Response ---")
        print(f"Model: {response.get('model', 'unknown')}")
        print(f"Response: {response.get('response', 'No response')}")
        print(f"Total tokens: {response.get('total_tokens', 0)}")
        print("---------------------\n")
        
        return True
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the inference service when run directly
    success = test_inference_service()
    
    if success:
        print("[SUCCESS] Inference service is working correctly!")
        sys.exit(0)
    else:
        print("[FAILED] Inference service test failed!")
        sys.exit(1)
