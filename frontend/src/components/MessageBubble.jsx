import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

const MessageBubble = ({ message, isExpanded, onToggleExpand }) => {
  const [copied, setCopied] = useState(false);
  const { role, content, timestamp, sources = [], isError } = message;
  
  const isUser = role === 'user';
  const hasSources = sources && sources.length > 0;
  
  const formattedTime = new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });

  const copyToClipboard = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`relative max-w-[80%] rounded-lg p-3 shadow-sm ${
          isUser 
            ? 'bg-primary-500 text-white' 
            : isError 
              ? 'bg-red-50 border border-red-100 text-red-800' 
              : 'bg-white border border-gray-100'
        }`}
      >
        {/* Message content */}
        <div className="prose prose-sm max-w-none">
          {isUser ? (
            <p className="m-0">{content}</p>
          ) : (
            <ReactMarkdown>{content}</ReactMarkdown>
          )}
        </div>
        
        {/* Sources section for assistant messages */}
        {!isUser && hasSources && (
          <div className="mt-3 pt-2 border-t border-gray-100">
            <button 
              onClick={onToggleExpand}
              className="text-xs flex items-center text-gray-500 hover:text-gray-700"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className={`h-4 w-4 mr-1 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
              {isExpanded ? 'Hide Sources' : 'Show Sources'} ({sources.length})
            </button>
            
            {isExpanded && (
              <div className="mt-2 space-y-2">
                {sources.map((source, index) => (
                  <div key={index} className="bg-gray-50 p-2 rounded text-xs">
                    <div className="font-medium text-gray-700">{source.title || 'Source'}</div>
                    <div className="text-gray-600 mt-1">{source.text}</div>
                    {source.page && (
                      <div className="text-gray-500 mt-1">Page: {source.page}</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {/* Timestamp and actions */}
        <div className={`flex justify-between items-center mt-1 text-xs ${
          isUser ? 'text-primary-200' : 'text-gray-400'
        }`}>
          <span>{formattedTime}</span>
          
          {!isUser && (
            <button 
              onClick={copyToClipboard} 
              className="flex items-center hover:text-gray-600"
              aria-label="Copy message"
            >
              {copied ? (
                <>
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    className="h-3 w-3 mr-1" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Copied
                </>
              ) : (
                <>
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    className="h-3 w-3 mr-1" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
