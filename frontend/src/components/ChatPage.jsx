import { useState, useEffect, useRef } from 'react';
import ChatWindow from './ChatWindow';
import ChatInput from './ChatInput';

const ChatPage = ({ serverStatus }) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      content: message,
      role: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    
    try {
      // Only attempt to send message if server is connected
      if (serverStatus === 'connected') {
        const response = await fetch('http://localhost:5000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message }),
        });
        
        if (!response.ok) {
          throw new Error('Server error');
        }
        
        const data = await response.json();
        
        // Add assistant message to chat
        const assistantMessage = {
          id: Date.now() + 1,
          content: data.response,
          role: 'assistant',
          timestamp: new Date().toISOString(),
          sources: data.sources || []
        };
        
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // If server is disconnected, show error message
        setTimeout(() => {
          const errorMessage = {
            id: Date.now() + 1,
            content: "Sorry, I can't process your message because the server is disconnected. Please check your connection and try again.",
            role: 'assistant',
            timestamp: new Date().toISOString(),
            isError: true
          };
          setMessages(prev => [...prev, errorMessage]);
        }, 1000);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        content: "Sorry, there was an error processing your message. Please try again.",
        role: 'assistant',
        timestamp: new Date().toISOString(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200">
        <div className="p-4 bg-primary-50 border-b border-primary-100">
          <h2 className="text-xl font-semibold text-primary-800">Health Consultation</h2>
          <p className="text-sm text-gray-600">Ask any health-related questions and get evidence-based answers</p>
        </div>
        
        <ChatWindow 
          messages={messages} 
          isTyping={isTyping} 
          messagesEndRef={messagesEndRef}
        />
        
        <div className="border-t border-gray-200 p-4">
          <ChatInput 
            onSendMessage={handleSendMessage} 
            disabled={isTyping || serverStatus !== 'connected'} 
            isTyping={isTyping}
          />
          {serverStatus !== 'connected' && (
            <div className="mt-2 text-center text-sm text-red-500">
              Server is disconnected. Chat functionality is limited.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
