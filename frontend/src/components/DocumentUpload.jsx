import { useState, useRef } from 'react';

const DocumentUpload = ({ onFilesSelected, onRemoveFile, files, uploading, disabled }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled || uploading) return;
    setIsDragging(true);
  };
  
  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };
  
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled || uploading) return;
    setIsDragging(true);
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (disabled || uploading) return;
    
    const droppedFiles = e.dataTransfer.files;
    handleFiles(droppedFiles);
  };
  
  const handleFileInputChange = (e) => {
    if (disabled || uploading) return;
    handleFiles(e.target.files);
  };
  
  const handleFiles = (selectedFiles) => {
    // Filter for PDF files
    const pdfFiles = Array.from(selectedFiles).filter(
      file => file.type === 'application/pdf'
    );
    
    if (pdfFiles.length > 0) {
      onFilesSelected(pdfFiles);
    } else if (selectedFiles.length > 0) {
      alert('Only PDF files are supported.');
    }
    
    // Reset the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  const handleBrowseClick = () => {
    if (disabled || uploading) return;
    fileInputRef.current?.click();
  };
  
  return (
    <div>
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center ${
          isDragging 
            ? 'border-primary-500 bg-primary-50' 
            : disabled 
              ? 'border-gray-200 bg-gray-50 opacity-60' 
              : 'border-gray-300 hover:border-primary-400 bg-white'
        } transition-colors ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleBrowseClick}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileInputChange}
          accept=".pdf"
          multiple
          className="hidden"
          disabled={disabled || uploading}
        />
        
        <div className="flex flex-col items-center justify-center">
          <svg 
            className={`h-16 w-16 mb-4 ${
              disabled ? 'text-gray-300' : 'text-primary-300'
            }`}
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={1.5} 
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
            />
          </svg>
          
          <h3 className={`text-lg font-medium mb-1 ${
            disabled ? 'text-gray-400' : 'text-gray-700'
          }`}>
            {isDragging ? 'Drop files here' : 'Drag and drop files here'}
          </h3>
          
          <p className={`text-sm mb-4 ${
            disabled ? 'text-gray-400' : 'text-gray-500'
          }`}>
            or <span className={`${
              disabled ? 'text-gray-400' : 'text-primary-500 font-medium'
            }`}>browse files</span> from your computer
          </p>
          
          <div className={`text-xs ${
            disabled ? 'text-gray-400' : 'text-gray-500'
          }`}>
            Supported file types: PDF
          </div>
          
          {disabled && (
            <div className="mt-3 text-sm text-red-500">
              Upload functionality is unavailable while server is disconnected
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;
