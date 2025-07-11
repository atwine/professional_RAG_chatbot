import { Link, useLocation } from 'react-router-dom';

const Header = ({ serverStatus }) => {
  const location = useLocation();
  
  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center mb-4 md:mb-0">
            <svg 
              className="h-8 w-8 text-primary-500 mr-2" 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
              <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
              <path d="M9 14h.01"></path>
              <path d="M15 14h.01"></path>
              <path d="M12 16v.01"></path>
            </svg>
            <h1 className="text-xl font-bold text-gray-800">Health AI Consultant</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <nav className="flex space-x-2">
              <Link 
                to="/chat" 
                className={`px-4 py-2 rounded-md ${
                  location.pathname === '/chat' 
                    ? 'bg-primary-100 text-primary-700 font-medium' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Chat
              </Link>
              <Link 
                to="/upload" 
                className={`px-4 py-2 rounded-md ${
                  location.pathname === '/upload' 
                    ? 'bg-primary-100 text-primary-700 font-medium' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Upload Documents
              </Link>
            </nav>
            
            <div className="flex items-center">
              <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
                serverStatus === 'connected' ? 'bg-green-500' : 
                serverStatus === 'disconnected' ? 'bg-red-500' : 
                'bg-yellow-500'
              }`}></span>
              <span className="text-sm text-gray-500">
                {serverStatus === 'connected' ? 'Server Connected' : 
                 serverStatus === 'disconnected' ? 'Server Disconnected' : 
                 'Checking Connection...'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
