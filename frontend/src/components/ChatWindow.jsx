import { useState } from 'react';
import MessageBubble from './MessageBubble';
import ReactMarkdown from 'react-markdown';

const ChatWindow = ({ messages, isTyping, messagesEndRef }) => {
  const [expandedSources, setExpandedSources] = useState({});

  const toggleSourceExpansion = (messageId) => {
    setExpandedSources(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }));
  };

  return (
    <div className="h-[500px] overflow-y-auto p-4 bg-gray-50">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
          <svg 
            className="h-12 w-12 text-primary-300 mb-3" 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={1.5} 
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" 
            />
          </svg>
          <h3 className="text-lg font-medium mb-1">Welcome to Health AI Consultant</h3>
          <p className="max-w-sm">
            Ask any health-related questions and receive evidence-based answers with sources.
          </p>
          <div className="mt-4 grid grid-cols-1 gap-2 w-full max-w-md">
            <button 
              className="bg-white border border-gray-300 rounded-lg px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              onClick={() => {
                const exampleQuestions = [
                  "What are the best ways to lower blood pressure naturally?",
                  "How many hours of sleep do adults need each night?",
                  "What are the symptoms of vitamin D deficiency?",
                  "Is intermittent fasting effective for weight loss?"
                ];
                const randomQuestion = exampleQuestions[Math.floor(Math.random() * exampleQuestions.length)];
                document.querySelector('textarea')?.focus();
                document.querySelector('textarea').value = randomQuestion;
              }}
            >
              Try an example question
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {messages.map(message => (
            <MessageBubble 
              key={message.id} 
              message={message} 
              isExpanded={expandedSources[message.id]} 
              onToggleExpand={() => toggleSourceExpansion(message.id)} 
            />
          ))}
          
          {isTyping && (
            <div className="flex items-start">
              <div className="bg-white rounded-lg p-3 shadow-sm max-w-[80%] ml-2">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 rounded-full bg-gray-300 animate-pulse"></div>
                  <div className="w-2 h-2 rounded-full bg-gray-300 animate-pulse delay-75"></div>
                  <div className="w-2 h-2 rounded-full bg-gray-300 animate-pulse delay-150"></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
