"""
Document handling API endpoints for Health AI Consultant.
Provides endpoints for uploading, processing, and managing documents.
"""
import os
import logging
import tempfile
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app

from services.document_processor import DocumentProcessor
from api.error_handlers import handle_invalid_request, handle_document_processing_error

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Blueprint
documents_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

# Initialize services
document_processor = DocumentProcessor()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}

def allowed_file(filename):
    """
    Check if the file extension is allowed.
    
    Args:
        filename: The name of the file to check.
        
    Returns:
        True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documents_bp.route('/upload', methods=['POST'])
def upload_document():
    """
    Upload and process a document.
    
    Request: multipart/form-data with 'file' field containing the document.
    
    Returns:
    {
        "success": true,
        "document_id": "unique_id",
        "filename": "uploaded_file.pdf",
        "metadata": {
            "title": "Document Title",
            "pages": 10,
            "chunks": 25
        }
    }
    """
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return handle_invalid_request("No file part in the request")
        
        file = request.files['file']
        
        # If user does not select file, browser might submit an empty file
        if file.filename == '':
            return handle_invalid_request("No file selected")
        
        # Check if the file is allowed
        if not file or not allowed_file(file.filename):
            return handle_invalid_request(f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # Create a temporary file to store the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
            file.save(temp.name)
            temp_path = temp.name
        
        try:
            # Process the document
            document_id, metadata = document_processor.process_document(
                file_path=temp_path,
                original_filename=secure_filename(file.filename)
            )
            
            # Remove the temporary file
            os.unlink(temp_path)
            
            # Return success response
            return jsonify({
                "success": True,
                "document_id": document_id,
                "filename": file.filename,
                "metadata": metadata
            })
            
        except Exception as e:
            # Clean up the temporary file if processing failed
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            logger.error(f"Error processing document: {e}")
            return handle_document_processing_error(e)
    
    except Exception as e:
        logger.error(f"Unexpected error in upload_document: {e}")
        return handle_document_processing_error(e)

@documents_bp.route('/', methods=['GET'])
def list_documents():
    """
    List all uploaded documents.
    
    Returns:
    {
        "documents": [
            {
                "id": "unique_id",
                "filename": "document1.pdf",
                "metadata": {...}
            },
            ...
        ]
    }
    """
    try:
        documents = document_processor.list_documents()
        return jsonify({"documents": documents})
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return handle_document_processing_error(e)

@documents_bp.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """
    Get information about a specific document.
    
    Returns:
    {
        "id": "unique_id",
        "filename": "document1.pdf",
        "metadata": {...}
    }
    """
    try:
        document = document_processor.get_document(document_id)
        if document:
            return jsonify(document)
        else:
            return handle_invalid_request(f"Document with ID {document_id} not found")
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        return handle_document_processing_error(e)

@documents_bp.route('/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """
    Delete a document from the system.
    
    Returns:
    {
        "success": true,
        "document_id": "unique_id"
    }
    """
    try:
        success = document_processor.delete_document(document_id)
        if success:
            return jsonify({
                "success": True,
                "document_id": document_id
            })
        else:
            return handle_invalid_request(f"Document with ID {document_id} not found")
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        return handle_document_processing_error(e)
