"""
Debug script to isolate which service or combination of services causes the segmentation fault.
This script tests each service initialization individually and in combinations.
"""
import logging
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

log = logging.getLogger(__name__)

def test_service_initialization():
    """Tests the initialization of each service individually and in combinations."""
    log.info("Starting service initialization tests...")
    
    # Test 1: Initialize VectorStoreService alone
    try:
        log.info("Test 1: Initializing VectorStoreService alone...")
        from services.vector_store import VectorStoreService
        vector_store = VectorStoreService()
        log.info("VectorStoreService initialized successfully.")
    except Exception as e:
        log.error(f"Error initializing VectorStoreService: {e}")
    
    # Test 2: Initialize QueryProcessor alone
    try:
        log.info("Test 2: Initializing QueryProcessor alone...")
        from services.query_processor import QueryProcessor
        query_processor = QueryProcessor()
        log.info("QueryProcessor initialized successfully.")
    except Exception as e:
        log.error(f"Error initializing QueryProcessor: {e}")
    
    # Test 3: Initialize InferenceService alone
    try:
        log.info("Test 3: Initializing InferenceService alone...")
        from services.inference import InferenceService
        inference_service = InferenceService()
        log.info("InferenceService initialized successfully.")
    except Exception as e:
        log.error(f"Error initializing InferenceService: {e}")
    
    # Test 4: Initialize VectorStoreService and QueryProcessor together
    try:
        log.info("Test 4: Initializing VectorStoreService and QueryProcessor together...")
        from services.vector_store import VectorStoreService
        from services.query_processor import QueryProcessor
        vector_store = VectorStoreService()
        query_processor = QueryProcessor()
        log.info("VectorStoreService and QueryProcessor initialized successfully together.")
    except Exception as e:
        log.error(f"Error initializing VectorStoreService and QueryProcessor together: {e}")
    
    # Test 5: Initialize VectorStoreService and InferenceService together
    try:
        log.info("Test 5: Initializing VectorStoreService and InferenceService together...")
        from services.vector_store import VectorStoreService
        from services.inference import InferenceService
        vector_store = VectorStoreService()
        inference_service = InferenceService()
        log.info("VectorStoreService and InferenceService initialized successfully together.")
    except Exception as e:
        log.error(f"Error initializing VectorStoreService and InferenceService together: {e}")
    
    # Test 6: Initialize QueryProcessor and InferenceService together
    try:
        log.info("Test 6: Initializing QueryProcessor and InferenceService together...")
        from services.query_processor import QueryProcessor
        from services.inference import InferenceService
        query_processor = QueryProcessor()
        inference_service = InferenceService()
        log.info("QueryProcessor and InferenceService initialized successfully together.")
    except Exception as e:
        log.error(f"Error initializing QueryProcessor and InferenceService together: {e}")
    
    # Test 7: Initialize all three services together
    try:
        log.info("Test 7: Initializing all three services together...")
        from services.vector_store import VectorStoreService
        from services.query_processor import QueryProcessor
        from services.inference import InferenceService
        vector_store = VectorStoreService()
        query_processor = QueryProcessor()
        inference_service = InferenceService()
        log.info("All three services initialized successfully together.")
    except Exception as e:
        log.error(f"Error initializing all three services together: {e}")
    
    log.info("Service initialization tests completed.")

if __name__ == "__main__":
    test_service_initialization()
