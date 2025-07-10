/**
 * Health AI Consultant API Client
 * 
 * This file contains example functions for interacting with the Health AI Consultant API
 * from a frontend application using the Fetch API.
 */

// Base URL for the API
const API_BASE_URL = 'http://localhost:5000';

/**
 * Check if the API is healthy
 * @returns {Promise<Object>} Health status response
 */
async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
}

/**
 * Send a question to the chat API
 * @param {string} question - The health-related question
 * @param {string} conversationId - Optional conversation ID for context
 * @param {boolean} stream - Whether to stream the response
 * @returns {Promise<Object|ReadableStream>} Chat response or stream
 */
async function sendChatQuestion(question, conversationId = null, stream = false) {
  try {
    // Prepare request body
    const requestBody = {
      question,
      stream
    };
    
    // Add conversation ID if provided
    if (conversationId) {
      requestBody.conversation_id = conversationId;
    }
    
    // Make the request
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || `Chat request failed: ${response.status} ${response.statusText}`);
    }
    
    // Handle streaming response
    if (stream) {
      return response.body;
    }
    
    // Handle regular JSON response
    return await response.json();
  } catch (error) {
    console.error('Chat error:', error);
    throw error;
  }
}

/**
 * Process a streaming chat response
 * @param {ReadableStream} stream - The response stream
 * @param {Function} onChunk - Callback for each chunk of text
 * @param {Function} onComplete - Callback when stream is complete
 * @param {Function} onError - Callback for errors
 */
async function processChatStream(stream, onChunk, onComplete, onError) {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  
  try {
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }
      
      // Decode the chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });
      
      // Process complete SSE messages
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || ''; // Keep the last incomplete chunk in the buffer
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.substring(6); // Remove 'data: ' prefix
          
          if (data === '[DONE]') {
            // End of stream
            if (onComplete) onComplete();
            return;
          }
          
          try {
            const parsedData = JSON.parse(data);
            if (onChunk) onChunk(parsedData);
          } catch (e) {
            console.warn('Error parsing SSE data:', e);
          }
        }
      }
    }
    
    // Process any remaining data in the buffer
    if (buffer && buffer.startsWith('data: ')) {
      const data = buffer.substring(6);
      
      if (data !== '[DONE]') {
        try {
          const parsedData = JSON.parse(data);
          if (onChunk) onChunk(parsedData);
        } catch (e) {
          console.warn('Error parsing SSE data:', e);
        }
      }
    }
    
    if (onComplete) onComplete();
  } catch (error) {
    console.error('Stream processing error:', error);
    if (onError) onError(error);
  }
}

/**
 * Upload a document to the API
 * @param {File} file - The file to upload
 * @param {Function} onProgress - Optional callback for upload progress
 * @returns {Promise<Object>} Upload response
 */
async function uploadDocument(file, onProgress = null) {
  try {
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    // Create request with progress tracking
    const xhr = new XMLHttpRequest();
    
    // Return a promise that resolves when the upload is complete
    return new Promise((resolve, reject) => {
      xhr.open('POST', `${API_BASE_URL}/api/documents/upload`);
      
      // Set up progress tracking
      if (onProgress) {
        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            onProgress(percentComplete);
          }
        };
      }
      
      // Handle response
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid response format'));
          }
        } else {
          try {
            const errorData = JSON.parse(xhr.responseText);
            reject(new Error(errorData.error?.message || `Upload failed: ${xhr.status} ${xhr.statusText}`));
          } catch (error) {
            reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
          }
        }
      };
      
      // Handle network errors
      xhr.onerror = () => {
        reject(new Error('Network error during upload'));
      };
      
      // Send the request
      xhr.send(formData);
    });
  } catch (error) {
    console.error('Document upload error:', error);
    throw error;
  }
}

/**
 * Get a list of all documents
 * @returns {Promise<Object>} List of documents
 */
async function listDocuments() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/documents/`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || `List documents failed: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('List documents error:', error);
    throw error;
  }
}

/**
 * Get details about a specific document
 * @param {string} documentId - ID of the document
 * @returns {Promise<Object>} Document details
 */
async function getDocumentDetails(documentId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || `Get document failed: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Get document error:', error);
    throw error;
  }
}

/**
 * Delete a document
 * @param {string} documentId - ID of the document to delete
 * @returns {Promise<Object>} Delete response
 */
async function deleteDocument(documentId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || `Delete document failed: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Delete document error:', error);
    throw error;
  }
}

// Example usage
async function exampleUsage() {
  try {
    // Check API health
    console.log('Checking API health...');
    const healthStatus = await checkHealth();
    console.log('Health status:', healthStatus);
    
    // Send a chat question
    console.log('Sending chat question...');
    const chatResponse = await sendChatQuestion('What are the benefits of regular exercise?');
    console.log('Chat response:', chatResponse);
    
    // Send a streaming chat question
    console.log('Sending streaming chat question...');
    const stream = await sendChatQuestion('How can I improve my diet?', null, true);
    
    processChatStream(
      stream,
      (chunk) => console.log('Received chunk:', chunk),
      () => console.log('Stream complete'),
      (error) => console.error('Stream error:', error)
    );
    
    // List documents
    console.log('Listing documents...');
    const documents = await listDocuments();
    console.log('Documents:', documents);
    
    // Upload a document (example - this won't actually run in this example)
    /*
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput.files.length > 0) {
      console.log('Uploading document...');
      const uploadResponse = await uploadDocument(
        fileInput.files[0],
        (progress) => console.log(`Upload progress: ${progress.toFixed(2)}%`)
      );
      console.log('Upload response:', uploadResponse);
      
      // Get document details
      console.log('Getting document details...');
      const documentDetails = await getDocumentDetails(uploadResponse.document_id);
      console.log('Document details:', documentDetails);
      
      // Delete document
      console.log('Deleting document...');
      const deleteResponse = await deleteDocument(uploadResponse.document_id);
      console.log('Delete response:', deleteResponse);
    }
    */
    
  } catch (error) {
    console.error('Example usage error:', error);
  }
}

// Export functions for use in other modules
export {
  checkHealth,
  sendChatQuestion,
  processChatStream,
  uploadDocument,
  listDocuments,
  getDocumentDetails,
  deleteDocument,
  exampleUsage
};
