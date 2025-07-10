"""
Ollama client service for Health AI Consultant.
Provides utilities for interacting with the Ollama API.
"""
import requests
import json
from typing import Dict, Any, Optional, Generator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with the Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama client.
        
        Args:
            base_url: Base URL for the Ollama API.
        """
        self.base_url = base_url
        logger.info(f"Initialized Ollama client with base URL: {base_url}")
    
    def list_models(self) -> Dict[str, Any]:
        """
        List available models from Ollama.
        
        Returns:
            Dictionary containing model information.
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error listing models: {e}")
            raise
    
    def generate(self, 
                 prompt: str, 
                 model: str = "llama3.1:8b", 
                 system: Optional[str] = None,
                 stream: bool = False,
                 **kwargs) -> Dict[str, Any]:
        """
        Generate a response from Ollama.
        
        Args:
            prompt: The prompt to send to the model.
            model: The model to use for generation.
            system: Optional system prompt.
            stream: Whether to stream the response.
            **kwargs: Additional parameters to pass to the Ollama API.
            
        Returns:
            Dictionary containing the response.
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            **kwargs
        }
        
        if system:
            payload["system"] = system
        
        try:
            if stream:
                return self._stream_response(url, payload)
            else:
                response = requests.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except requests.RequestException as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def _stream_response(self, url: str, payload: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Stream response from Ollama API.
        
        Args:
            url: API endpoint URL.
            payload: Request payload.
            
        Yields:
            Dictionaries containing response chunks.
        """
        try:
            with requests.post(url, json=payload, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        yield json.loads(line)
        except requests.RequestException as e:
            logger.error(f"Error streaming response: {e}")
            raise

# Test function to verify Ollama connection
def test_ollama_connection(base_url: str = "http://localhost:11434") -> bool:
    """
    Test connection to Ollama API.
    
    Args:
        base_url: Base URL for the Ollama API.
        
    Returns:
        True if connection is successful, False otherwise.
    """
    client = OllamaClient(base_url)
    try:
        models = client.list_models()
        logger.info(f"Successfully connected to Ollama. Available models: {models}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        return False

if __name__ == "__main__":
    # Test the Ollama connection when run directly
    import sys
    import os
    import sys
    
    # Add the project root directory to the Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    
    from config import config
    
    base_url = config.OLLAMA_BASE_URL
    success = test_ollama_connection(base_url)
    
    if success:
        print("[SUCCESS] Successfully connected to Ollama API!")
        sys.exit(0)
    else:
        print("[FAILED] Failed to connect to Ollama API!")
        sys.exit(1)
