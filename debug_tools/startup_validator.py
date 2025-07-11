"""
Startup validation script for Health AI Consultant backend.
Validates all critical services before starting the main Flask application.
"""
import sys
import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_ollama_connection() -> Dict[str, Any]:
    """Validate Ollama server connection and model availability."""
    try:
        import ollama
        client = ollama.Client(host="http://localhost:11434", timeout=5)
        
        # Test basic connection
        models = client.list()
        logger.info(f"Ollama connection successful. Found {len(models.models)} models")
        
        # Check for required embedding model
        model_names = [model.name for model in models.models]
        required_model = "nomic-embed-text"
        
        if any(required_model in name for name in model_names):
            logger.info(f"Required embedding model '{required_model}' found")
            return {"status": "healthy", "models": len(models.models)}
        else:
            logger.warning(f"Required embedding model '{required_model}' not found")
            return {"status": "degraded", "models": len(models.models), "warning": "Missing embedding model"}
            
    except Exception as e:
        logger.error(f"Ollama validation failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

def validate_vector_store() -> Dict[str, Any]:
    """Validate vector store initialization without blocking operations."""
    try:
        import os
        from config import config
        
        # Check if database path exists and is accessible
        db_path = config.VECTOR_DB_PATH
        if not os.path.exists(db_path):
            os.makedirs(db_path, exist_ok=True)
            logger.info(f"Created vector store directory: {db_path}")
        
        # Test basic ChromaDB import
        import chromadb
        logger.info("ChromaDB import successful")
        
        return {"status": "healthy", "db_path": db_path}
        
    except Exception as e:
        logger.error(f"Vector store validation failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

def validate_flask_imports() -> Dict[str, Any]:
    """Validate all Flask blueprint imports."""
    try:
        # Test critical imports
        from flask import Flask
        from api.chat import chat_bp
        from api.documents import documents_bp
        from services.performance_monitor import performance_monitor
        
        logger.info("All Flask imports successful")
        return {"status": "healthy"}
        
    except Exception as e:
        logger.error(f"Flask import validation failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

def run_startup_validation() -> bool:
    """Run all startup validations and return True if safe to proceed."""
    logger.info("Starting backend validation...")
    
    validations = {
        "flask_imports": validate_flask_imports(),
        "vector_store": validate_vector_store(),
        "ollama": validate_ollama_connection()
    }
    
    # Log results
    all_healthy = True
    for service, result in validations.items():
        status = result.get("status", "unknown")
        if status == "healthy":
            logger.info(f"✅ {service}: {status}")
        elif status == "degraded":
            logger.warning(f"⚠️  {service}: {status} - {result.get('warning', '')}")
        else:
            logger.error(f"❌ {service}: {status} - {result.get('error', '')}")
            all_healthy = False
    
    if all_healthy:
        logger.info("🚀 All validations passed. Backend is ready to start.")
        return True
    else:
        logger.error("❌ Some validations failed. Check logs above.")
        return False

if __name__ == "__main__":
    if run_startup_validation():
        sys.exit(0)
    else:
        sys.exit(1)
