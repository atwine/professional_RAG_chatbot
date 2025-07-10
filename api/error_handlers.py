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
    # Ollama-related errors
    OLLAMA_CONNECTION_ERROR = "OLLAMA_CONNECTION_ERROR"
    OLLAMA_GENERATION_ERROR = "OLLAMA_GENERATION_ERROR"
    OLLAMA_TIMEOUT_ERROR = "OLLAMA_TIMEOUT_ERROR"
    OLLAMA_MODEL_NOT_FOUND = "OLLAMA_MODEL_NOT_FOUND"
    
    # Request validation errors
    INVALID_REQUEST = "INVALID_REQUEST"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FIELD_VALUE = "INVALID_FIELD_VALUE"
    REQUEST_TOO_LARGE = "REQUEST_TOO_LARGE"
    
    # Vector database errors
    VECTOR_DB_ERROR = "VECTOR_DB_ERROR"
    VECTOR_DB_CONNECTION_ERROR = "VECTOR_DB_CONNECTION_ERROR"
    VECTOR_DB_QUERY_ERROR = "VECTOR_DB_QUERY_ERROR"
    VECTOR_DB_INSERT_ERROR = "VECTOR_DB_INSERT_ERROR"
    
    # Document processing errors
    DOCUMENT_PROCESSING_ERROR = "DOCUMENT_PROCESSING_ERROR"
    DOCUMENT_PARSE_ERROR = "DOCUMENT_PARSE_ERROR"
    DOCUMENT_TOO_LARGE = "DOCUMENT_TOO_LARGE"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    CORRUPT_DOCUMENT = "CORRUPT_DOCUMENT"
    
    # Rate limiting and quota errors
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    
    # Authentication and authorization errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    
    # Server errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"


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
                "code": ErrorCodes.OLLAMA_TIMEOUT_ERROR,
                "message": "Ollama API request timed out. The model may be overloaded or unavailable.",
                "details": str(error)
            }
        }), 504  # Gateway Timeout
    
    elif isinstance(error, requests.HTTPError):
        # Check for specific HTTP error codes
        if hasattr(error, 'response') and error.response is not None:
            if error.response.status_code == 404:
                return jsonify({
                    "error": {
                        "code": ErrorCodes.OLLAMA_MODEL_NOT_FOUND,
                        "message": "The requested Ollama model was not found.",
                        "details": str(error)
                    }
                }), 404  # Not Found
            else:
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


def register_error_handlers(app):
    """
    Register error handlers with the Flask app.
    
    Args:
        app: The Flask application instance.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return handle_invalid_request("Bad request", str(error))
    
    @app.errorhandler(404)
    def not_found(error):
        return handle_invalid_request("Resource not found", str(error))
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return handle_invalid_request("Method not allowed", str(error))
    
    @app.errorhandler(500)
    def server_error(error):
        return handle_internal_server_error(error)
    
    logger.info("Error handlers registered")
    return app
