import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

log = logging.getLogger(__name__)

def test_vector_store_initialization():
    """Tests the initialization of the VectorStoreService."""
    log.info("Starting vector store initialization test...")
    try:
        # We import here to ensure all modules are loaded fresh for the test
        from services.vector_store import VectorStoreService
        log.info("Imported VectorStoreService successfully.")
        
        vector_store = VectorStoreService()
        log.info("Successfully initialized VectorStoreService.")
        
        log.info("Vector store test completed successfully.")
        return True
    except Exception as e:
        log.error(f"An error occurred during vector store initialization: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    test_vector_store_initialization()
