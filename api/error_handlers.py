"""
Error handling utilities for the Health AI Consultant API.
"""
import logging
from typing import Dict, Any, Tuple
from flask import jsonify
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define error codes and messages
class ErrorCodes:
    """Error codes for the Health AI Consultant API."""
    OLLAMA_CONNECTION_ERROR = "OLLAMA_CONNECTION_ERROR"
    OLLAMA_GENERATION_ERROR = "OLLAMA_GENERATION_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    VECTOR_DB_ERROR = "VECTOR_DB_ERROR"
    DOCUMENT_PROCESSING_ERROR = "DOCUMENT_PROCESSING_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


def handle_ollama_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """
    Handle errors from the Ollama API.
    
    Args:
        error: The exception raised.
        
    Returns:
        Tuple containing error response and HTTP status code.
    """
    logger.error(f"Ollama API error: {error}")
    
    if isinstance(error, requests.ConnectionError):
        return jsonify({
            "error": {
                "code": ErrorCodes.OLLAMA_CONNECTION_ERROR,
                "message": "Failed to connect to Ollama API. Please ensure Ollama is running.",
                "details": str(error)
            }
        }), 503  # Service Unavailable
    
    elif isinstance(error, requests.Timeout):
        return jsonify({
            "error": {
                "code": ErrorCodes.OLLAMA_CONNECTION_ERROR,
                "message": "Ollama API request timed out. The model may be overloaded or unavailable.",
                "details": str(error)
            }
        }), 504  # Gateway Timeout
    
    elif isinstance(error, requests.HTTPError):
        return jsonify({
            "error": {
                "code": ErrorCodes.OLLAMA_GENERATION_ERROR,
                "message": "Ollama API returned an error response.",
                "details": str(error)
            }
        }), 502  # Bad Gateway
    
    else:
        return jsonify({
            "error": {
                "code": ErrorCodes.OLLAMA_GENERATION_ERROR,
                "message": "An error occurred while generating a response from Ollama.",
                "details": str(error)
            }
        }), 500  # Internal Server Error


def handle_vector_db_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """
    Handle errors from the vector database.
    
    Args:
        error: The exception raised.
        
    Returns:
        Tuple containing error response and HTTP status code.
    """
    logger.error(f"Vector database error: {error}")
    
    return jsonify({
        "error": {
            "code": ErrorCodes.VECTOR_DB_ERROR,
            "message": "An error occurred while accessing the vector database.",
            "details": str(error)
        }
    }), 500  # Internal Server Error


def handle_document_processing_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """
    Handle errors from document processing.
    
    Args:
        error: The exception raised.
        
    Returns:
        Tuple containing error response and HTTP status code.
    """
    logger.error(f"Document processing error: {error}")
    
    return jsonify({
        "error": {
            "code": ErrorCodes.DOCUMENT_PROCESSING_ERROR,
            "message": "An error occurred while processing the document.",
            "details": str(error)
        }
    }), 500  # Internal Server Error


def handle_invalid_request(message: str, details: str = "") -> Tuple[Dict[str, Any], int]:
    """
    Handle invalid request errors.
    
    Args:
        message: The error message.
        details: Additional details about the error.
        
    Returns:
        Tuple containing error response and HTTP status code.
    """
    logger.warning(f"Invalid request: {message} - {details}")
    
    return jsonify({
        "error": {
            "code": ErrorCodes.INVALID_REQUEST,
            "message": message,
            "details": details
        }
    }), 400  # Bad Request


def handle_internal_server_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """
    Handle general internal server errors.
    
    Args:
        error: The exception raised.
        
    Returns:
        Tuple containing error response and HTTP status code.
    """
    logger.error(f"Internal server error: {error}")
    
    return jsonify({
        "error": {
            "code": ErrorCodes.INTERNAL_SERVER_ERROR,
            "message": "An internal server error occurred.",
            "details": str(error)
        }
    }), 500  # Internal Server Error
