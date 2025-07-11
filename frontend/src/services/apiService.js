/**
 * API Service for Health AI Consultant
 * Handles all communication with the backend API
 */

const API_BASE_URL = 'http://localhost:5000/api';
const DEFAULT_TIMEOUT = 30000; // 30 seconds

/**
 * Helper for making GET requests
 * @param {string} endpoint - API endpoint to call
 * @param {Object} options - Additional fetch options
 * @returns {Promise<any>} - Parsed response data
 */
export const get = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Set up request with timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), options.timeout || DEFAULT_TIMEOUT);
  
  try {
    console.log(`[API] GET ${url}`);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
      ...options,
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log(`[API] Response from ${endpoint}:`, data);
    return data;
  } catch (error) {
    console.error(`[API] Error in GET ${endpoint}:`, error);
    
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.');
    }
    
    throw error;
  }
};

/**
 * Helper for making POST requests
 * @param {string} endpoint - API endpoint to call
 * @param {Object} data - Data to send in request body
 * @param {Object} options - Additional fetch options
 * @returns {Promise<any>} - Parsed response data
 */
export const post = async (endpoint, data, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Set up request with timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), options.timeout || DEFAULT_TIMEOUT);
  
  try {
    console.log(`[API] POST ${url}`, data);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(data),
      signal: controller.signal,
      ...options,
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    const responseData = await response.json();
    console.log(`[API] Response from ${endpoint}:`, responseData);
    return responseData;
  } catch (error) {
    console.error(`[API] Error in POST ${endpoint}:`, error);
    
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.');
    }
    
    throw error;
  }
};

/**
 * Chat API methods
 */
export const chatApi = {
  /**
   * Send a message to the chat API
   * @param {string} message - User message
   * @returns {Promise<Object>} - Response with assistant message and sources
   */
  sendMessage: async (message) => {
    return post('/chat', { message });
  }
};

/**
 * Document API methods
 */
export const documentApi = {
  /**
   * Upload a document to the API
   * @param {File} file - File to upload
   * @param {Function} onProgress - Progress callback
   * @returns {Promise<Object>} - Response with document ID
   */
  uploadDocument: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const percentComplete = Math.round((event.loaded / event.total) * 100);
          onProgress(percentComplete);
        }
      });
      
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid response format'));
          }
        } else {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      };
      
      xhr.onerror = () => reject(new Error('Network error during upload'));
      xhr.onabort = () => reject(new Error('Upload aborted'));
      xhr.ontimeout = () => reject(new Error('Upload timed out'));
      
      xhr.open('POST', `${API_BASE_URL}/documents/upload`);
      xhr.timeout = DEFAULT_TIMEOUT;
      xhr.send(formData);
    });
  },
  
  /**
   * Get all documents
   * @returns {Promise<Array>} - List of documents
   */
  getDocuments: async () => {
    return get('/documents');
  }
};

/**
 * Health check API
 */
export const healthApi = {
  /**
   * Check if the API is healthy
   * @returns {Promise<Object>} - Health status
   */
  checkHealth: async () => {
    try {
      const response = await fetch('http://localhost:5000/health');
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('[API] Health check failed:', error);
      throw error;
    }
  }
};

export default {
  get,
  post,
  chatApi,
  documentApi,
  healthApi
};
