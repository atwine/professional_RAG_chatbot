import { Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Header from './components/Header';
import ChatPage from './components/ChatPage';
import UploadPage from './components/UploadPage';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [serverStatus, setServerStatus] = useState('unknown');

  // Check if the backend server is running
  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const response = await fetch('http://localhost:5000/health');
        const data = await response.json();
        setServerStatus(data.status === 'healthy' ? 'connected' : 'error');
      } catch (error) {
        console.error('Error connecting to server:', error);
        setServerStatus('disconnected');
      } finally {
        setIsLoading(false);
      }
    };

    checkServerStatus();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header serverStatus={serverStatus} />
      
      <main className="container mx-auto px-4 py-8">
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
          </div>
        ) : (
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<ChatPage serverStatus={serverStatus} />} />
            <Route path="/upload" element={<UploadPage serverStatus={serverStatus} />} />
          </Routes>
        )}
      </main>

      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
          &copy; {new Date().getFullYear()} Health AI Consultant. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

export default App;
