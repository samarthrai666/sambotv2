'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface HeaderProps {
  showActions?: boolean;
}

export default function Header({ showActions = true }: HeaderProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check authentication status when component mounts
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      setIsLoggedIn(!!token);
    };
    
    // Use setTimeout to avoid SSR issues with localStorage
    const timer = setTimeout(() => {
      checkAuth();
    }, 0);
    
    return () => clearTimeout(timer);
  }, []);

  const handleLogin = () => {
    setIsLoading(true);
    router.push('/login');
  };

  const handleSignalPage = () => {
    router.push('/selection');
  };

  const handleLogout = () => {
    // Clear token and other user data
    localStorage.removeItem('token');
    localStorage.removeItem('tradingSignals');
    
    // Redirect to home page
    router.push('/');
  };

  return (
    <>
      {/* Green gradient line at the top for visual interest */}
      <div className="h-1 bg-gradient-to-r from-green-400 to-green-600 w-full"></div>
      
      <header className="bg-white sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              {/* Logo - A circular icon with "S" and a graph line */}
              <Link href="/" className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-green-500 to-green-600 flex items-center justify-center mr-2 shadow-md">
                  <div className="text-white font-bold text-lg relative">
                    S
                    <div className="absolute top-0 right-0 h-1/2 w-1/2">
                      <div className="absolute bottom-0 right-0 w-full h-1/3 bg-white transform rotate-45 rounded-full"></div>
                    </div>
                  </div>
                </div>
                <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-500 to-green-700">
                  Sambot
                </span>
                <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full animate-pulse">
                  BETA
                </span>
              </Link>
            </div>
            
            {showActions && (
              <div className="flex items-center space-x-4">
                {isLoggedIn ? (
                  <>
                    <button
                      onClick={handleSignalPage}
                      className="text-green-600 hover:text-green-800 font-medium transition-colors duration-300 px-4 py-2 rounded hover:bg-green-50"
                    >
                      Trading Signals
                    </button>
                    
                    <button
                      onClick={handleLogout}
                      className="text-gray-600 hover:text-gray-800 transition-colors duration-300 px-4 py-2 rounded hover:bg-gray-50"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <button
                    onClick={handleLogin}
                    className={`px-4 py-2 rounded-md bg-green-600 text-white hover:bg-green-700 transform hover:scale-105 transition-all duration-300 shadow-md ${
                      isLoading ? 'opacity-75 cursor-not-allowed' : ''
                    }`}
                    disabled={isLoading}
                  >
                    {isLoading ? 'Loading...' : 'Login'}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </header>
    </>
  );
}