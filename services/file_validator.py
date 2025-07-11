"""
File validation service for Health AI Consultant.
Provides utilities for validating file uploads and ensuring security.
"""
import os
import logging
import mimetypes
from typing import Tuple, List, Optional
from werkzeug.datastructures import FileStorage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileValidator:
    """Service for validating file uploads and ensuring security."""
    
    def __init__(self, 
                 allowed_extensions: List[str] = None,
                 allowed_mime_types: List[str] = None,
                 max_file_size_mb: int = 10):
        """
        Initialize the file validator.
        
        Args:
            allowed_extensions: List of allowed file extensions (e.g., ['pdf', 'txt']).
            allowed_mime_types: List of allowed MIME types (e.g., ['application/pdf', 'text/plain']).
            max_file_size_mb: Maximum file size in megabytes.
        """
        self.allowed_extensions = allowed_extensions or ['pdf', 'txt', 'docx']
        self.allowed_mime_types = allowed_mime_types or [
            'application/pdf',
            'text/plain',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        logger.info(f"Initialized file validator with allowed extensions: {self.allowed_extensions}")
    
    def validate_file(self, file: FileStorage) -> Tuple[bool, Optional[str]]:
        """
        Validate a file upload.
        
        Args:
            file: The uploaded file.
            
        Returns:
            Tuple containing:
                - Boolean indicating if the file is valid.
                - Error message if the file is invalid, None otherwise.
        """
        # Check if file exists
        if not file:
            return False, "No file provided"
        
        # Check file size
        if self._get_file_size(file) > self.max_file_size_bytes:
            max_size_mb = self.max_file_size_bytes / (1024 * 1024)
            return False, f"File size exceeds maximum allowed size of {max_size_mb} MB"
        
        # Check file extension
        if not self._has_allowed_extension(file.filename):
            return False, f"File extension not allowed. Allowed extensions: {', '.join(self.allowed_extensions)}"
        
        # Check MIME type
        mime_type = self._get_mime_type(file)
        if mime_type not in self.allowed_mime_types:
            return False, f"File type not allowed. Detected MIME type: {mime_type}"
        
        # Check for potential malicious content
        if self._potentially_malicious(file):
            return False, "File appears to be potentially malicious"
        
        return True, None
    
    def _get_file_size(self, file: FileStorage) -> int:
        """
        Get the size of a file in bytes.
        
        Args:
            file: The file to check.
            
        Returns:
            File size in bytes.
        """
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)  # Reset file pointer
        return size
    
    def _has_allowed_extension(self, filename: str) -> bool:
        """
        Check if a filename has an allowed extension.
        
        Args:
            filename: The filename to check.
            
        Returns:
            Boolean indicating if the file has an allowed extension.
        """
        if not filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return extension in self.allowed_extensions
    
    def _get_mime_type(self, file: FileStorage) -> str:
        """
        Get the MIME type of a file.
        
        Args:
            file: The file to check.
            
        Returns:
            MIME type string.
        """
        # Use Python's built-in mimetypes module instead of python-magic
        if not file.filename:
            return 'application/octet-stream'
            
        # Initialize mimetypes if not already done
        if not mimetypes.inited:
            mimetypes.init()
            
        # Get MIME type based on file extension
        mime_type, _ = mimetypes.guess_type(file.filename)
        
        # Default to octet-stream if type couldn't be determined
        if mime_type is None:
            mime_type = 'application/octet-stream'
            
        logger.info(f"Detected MIME type for {file.filename}: {mime_type}")
        return mime_type
    
    def _potentially_malicious(self, file: FileStorage) -> bool:
        """
        Check if a file is potentially malicious.
        
        Args:
            file: The file to check.
            
        Returns:
            Boolean indicating if the file is potentially malicious.
        """
        # This is a basic implementation that could be expanded with more sophisticated checks
        # For example, integrating with a virus scanning API or library
        
        # Check for executable content in PDFs
        mime_type = self._get_mime_type(file)
        
        # Only perform content checks for PDFs
        if mime_type == 'application/pdf':
            # Read file content
            try:
                file_content = file.read().lower()
                file.seek(0)  # Reset file pointer
                
                # Check for JavaScript or executable actions in PDF
                suspicious_patterns = [b'/js', b'/javascript', b'/action', b'/launch', b'/openaction', b'/aa']
                for pattern in suspicious_patterns:
                    if pattern in file_content:
                        logger.warning(f"Potentially malicious content detected in PDF: {pattern}")
                        return True
            except Exception as e:
                logger.error(f"Error checking file content: {e}")
                # If we can't check the content, assume it's safe to avoid false positives
                return False
        
        return False

# Create a singleton instance with default settings
file_validator = FileValidator()
