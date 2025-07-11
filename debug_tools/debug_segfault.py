"""
Debug script to isolate segmentation fault in Flask application.
This script tests different components in isolation to identify the cause.
"""
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_flask_minimal():
    """Test minimal Flask app without any of our services."""
    logger.info("Testing minimal Flask app...")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/test')
        def test():
            return "Test successful"
        
        logger.info("Minimal Flask app created successfully")
        return True
    except Exception as e:
        logger.error(f"Error in minimal Flask app: {e}")
        return False

def test_vector_store():
    """Test vector store service in isolation."""
    logger.info("Testing vector store service...")
    
    try:
        from services.vector_store import VectorStoreService
        vector_store = VectorStoreService()
        logger.info("Vector store service initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error in vector store service: {e}")
        return False

def test_query_processor():
    """Test query processor in isolation."""
    logger.info("Testing query processor...")
    
    try:
        from services.query_processor import QueryProcessor
        processor = QueryProcessor()
        logger.info("Query processor initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error in query processor: {e}")
        return False

def test_inference_service():
    """Test inference service in isolation."""
    logger.info("Testing inference service...")
    
    try:
        from services.inference import InferenceService
        inference = InferenceService()
        logger.info("Inference service initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error in inference service: {e}")
        return False

def test_combined_services():
    """Test all services together but without Flask."""
    logger.info("Testing all services together...")
    
    try:
        from services.vector_store import VectorStoreService
        from services.query_processor import QueryProcessor
        from services.inference import InferenceService
        
        vector_store = VectorStoreService()
        processor = QueryProcessor()
        inference = InferenceService()
        
        logger.info("All services initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error in combined services: {e}")
        return False

def test_flask_with_blueprints():
    """Test Flask with blueprints but without service initialization."""
    logger.info("Testing Flask with blueprints...")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        
        # Import blueprints without initializing services
        from api.chat import chat_bp
        from api.documents import documents_bp
        
        # Register blueprints
        app.register_blueprint(chat_bp)
        app.register_blueprint(documents_bp)
        
        logger.info("Flask with blueprints initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error in Flask with blueprints: {e}")
        return False

def test_flask_with_one_service(service_name):
    """Test Flask with just one service."""
    logger.info(f"Testing Flask with {service_name}...")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        
        if service_name == "vector_store":
            from services.vector_store import VectorStoreService
            vector_store = VectorStoreService()
        elif service_name == "query_processor":
            from services.query_processor import QueryProcessor
            processor = QueryProcessor()
        elif service_name == "inference":
            from services.inference import InferenceService
            inference = InferenceService()
        
        logger.info(f"Flask with {service_name} initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error in Flask with {service_name}: {e}")
        return False

def run_tests():
    """Run all tests in sequence."""
    tests = [
        ("Minimal Flask", test_flask_minimal),
        ("Vector Store", test_vector_store),
        ("Query Processor", test_query_processor),
        ("Inference Service", test_inference_service),
        ("Combined Services", test_combined_services),
        ("Flask with Blueprints", test_flask_with_blueprints),
        ("Flask with Vector Store", lambda: test_flask_with_one_service("vector_store")),
        ("Flask with Query Processor", lambda: test_flask_with_one_service("query_processor")),
        ("Flask with Inference", lambda: test_flask_with_one_service("inference"))
    ]
    
    results = {}
    
    for name, test_func in tests:
        logger.info(f"Running test: {name}")
        try:
            success = test_func()
            results[name] = "SUCCESS" if success else "FAILED"
        except Exception as e:
            logger.error(f"Exception in {name}: {e}")
            results[name] = f"EXCEPTION: {str(e)}"
        
        # Add a small delay between tests
        time.sleep(1)
    
    # Print summary
    logger.info("\n--- TEST RESULTS SUMMARY ---")
    for name, result in results.items():
        logger.info(f"{name}: {result}")
    
    return results

if __name__ == "__main__":
    logger.info("Starting segmentation fault debugging...")
    results = run_tests()
    
    # Check if any test failed with segmentation fault
    # Note: We can't directly catch segfaults, but we can check if a test didn't complete
    for name, result in results.items():
        if "EXCEPTION" in result and "Segmentation fault" in result:
            logger.error(f"Segmentation fault detected in: {name}")
    
    logger.info("Debugging complete")
