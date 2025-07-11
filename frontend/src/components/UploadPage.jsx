import { useState, useRef } from 'react';
import DocumentUpload from './DocumentUpload';

const UploadPage = ({ serverStatus }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadResults, setUploadResults] = useState([]);
  
  const handleFilesSelected = (selectedFiles) => {
    // Convert FileList to array and filter out any non-PDF files
    const fileArray = Array.from(selectedFiles).filter(
      file => file.type === 'application/pdf'
    );
    
    // Initialize progress tracking for each file
    const initialProgress = {};
    fileArray.forEach(file => {
      initialProgress[file.name] = 0;
    });
    
    setFiles(fileArray);
    setUploadProgress(initialProgress);
    setUploadResults([]);
  };
  
  const handleRemoveFile = (fileName) => {
    setFiles(prev => prev.filter(file => file.name !== fileName));
    
    // Also remove from progress and results if present
    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[fileName];
      return newProgress;
    });
    
    setUploadResults(prev => prev.filter(result => result.fileName !== fileName));
  };
  
  const handleUpload = async () => {
    if (files.length === 0 || uploading || serverStatus !== 'connected') return;
    
    setUploading(true);
    const results = [];
    
    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const xhr = new XMLHttpRequest();
        
        // Track upload progress
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const percentComplete = Math.round((event.loaded / event.total) * 100);
            setUploadProgress(prev => ({
              ...prev,
              [file.name]: percentComplete
            }));
          }
        });
        
        // Create a promise to handle the XHR request
        const uploadPromise = new Promise((resolve, reject) => {
          xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              resolve(JSON.parse(xhr.responseText));
            } else {
              reject(new Error(`Upload failed with status ${xhr.status}`));
            }
          };
          
          xhr.onerror = () => reject(new Error('Network error during upload'));
          xhr.onabort = () => reject(new Error('Upload aborted'));
        });
        
        // Start the request
        xhr.open('POST', 'http://localhost:5000/api/documents/upload');
        xhr.send(formData);
        
        // Wait for the upload to complete
        const response = await uploadPromise;
        
        results.push({
          fileName: file.name,
          success: true,
          documentId: response.document_id,
          message: 'Document uploaded successfully'
        });
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error);
        
        results.push({
          fileName: file.name,
          success: false,
          message: error.message || 'Upload failed'
        });
      }
    }
    
    setUploadResults(results);
    setUploading(false);
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200">
        <div className="p-4 bg-primary-50 border-b border-primary-100">
          <h2 className="text-xl font-semibold text-primary-800">Upload Health Documents</h2>
          <p className="text-sm text-gray-600">Upload PDF documents to enhance the AI's knowledge base</p>
        </div>
        
        <div className="p-6">
          <DocumentUpload 
            onFilesSelected={handleFilesSelected}
            onRemoveFile={handleRemoveFile}
            files={files}
            uploading={uploading}
            disabled={serverStatus !== 'connected'}
          />
          
          {files.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-medium mb-3">Selected Files</h3>
              <div className="space-y-3">
                {files.map(file => (
                  <div 
                    key={file.name} 
                    className="bg-gray-50 rounded-lg p-3 flex items-center justify-between"
                  >
                    <div className="flex items-center">
                      <svg 
                        className="h-8 w-8 text-red-500 mr-3" 
                        xmlns="http://www.w3.org/2000/svg" 
                        viewBox="0 0 24 24" 
                        fill="currentColor"
                      >
                        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-9.5 8.5h-3v-1h3V8h-3V7h3V5.5H5v13h4.5V13zm2.5 5.5h-1.5V14h-1v3H9v-3H7.5v4.5H14v-6h1.5v4.5zm3.5-1h-1.5V13H13v2.5h2.5V17H13v1.5h3.5z" />
                      </svg>
                      <div>
                        <div className="font-medium">{file.name}</div>
                        <div className="text-sm text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center">
                      {uploading && (
                        <div className="mr-4 w-24">
                          <div className="h-2 bg-gray-200 rounded-full">
                            <div 
                              className="h-full bg-primary-500 rounded-full" 
                              style={{ width: `${uploadProgress[file.name] || 0}%` }}
                            ></div>
                          </div>
                          <div className="text-xs text-center mt-1">
                            {uploadProgress[file.name] || 0}%
                          </div>
                        </div>
                      )}
                      
                      {uploadResults.find(r => r.fileName === file.name) ? (
                        <div className={`text-sm ${
                          uploadResults.find(r => r.fileName === file.name)?.success
                            ? 'text-green-600'
                            : 'text-red-600'
                        }`}>
                          {uploadResults.find(r => r.fileName === file.name)?.success
                            ? 'Uploaded'
                            : 'Failed'}
                        </div>
                      ) : (
                        <button
                          onClick={() => handleRemoveFile(file.name)}
                          disabled={uploading}
                          className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
                        >
                          <svg 
                            className="h-5 w-5" 
                            xmlns="http://www.w3.org/2000/svg" 
                            viewBox="0 0 20 20" 
                            fill="currentColor"
                          >
                            <path 
                              fillRule="evenodd" 
                              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" 
                              clipRule="evenodd" 
                            />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-6">
                <button
                  onClick={handleUpload}
                  disabled={files.length === 0 || uploading || serverStatus !== 'connected'}
                  className={`px-4 py-2 rounded-md ${
                    files.length > 0 && !uploading && serverStatus === 'connected'
                      ? 'bg-primary-500 text-white hover:bg-primary-600'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  } transition-colors`}
                >
                  {uploading ? 'Uploading...' : 'Upload Files'}
                </button>
                
                {serverStatus !== 'connected' && (
                  <div className="mt-2 text-sm text-red-500">
                    Server is disconnected. Upload functionality is unavailable.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
