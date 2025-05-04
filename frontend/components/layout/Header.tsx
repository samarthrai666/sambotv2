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
  const [currentTime, setCurrentTime] = useState(new Date());

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
    
    // Update time every second for the digital clock
    const clockInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    return () => {
      clearTimeout(timer);
      clearInterval(clockInterval);
    };
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
      {/* Solid green line at the top - no animation */}
      <div className="h-1 bg-green-500 w-full"></div>
      
      <header className="bg-white sticky top-0 z-10 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              {/* Futuristic Logo - kept the rotation but removed other animations */}
              <Link href="/" className="flex items-center group">
                <div className="relative w-12 h-12 flex items-center justify-center">
                  {/* Fixed outer ring - no animation */}
                  <div className="absolute w-12 h-12 rounded-full border-2 border-green-400 opacity-80"></div>
                  
                  {/* Inner rotating circle - kept this animation */}
                  <div className="absolute w-10 h-10 rounded-full border-t-2 border-r-2 border-green-500 animate-spin"></div>
                  
                  {/* Core circle with gradient */}
                  <div className="absolute w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-green-600 shadow-md flex items-center justify-center z-10">
                    <span className="text-white font-bold text-lg tracking-tighter">S</span>
                  </div>
                </div>
                
                {/* Text with gradient - no animation */}
                <div className="ml-3 flex flex-col">
                  <span className="text-2xl font-bold text-green-600">
                    SamarAI
                  </span>
                  <span className="text-xs text-green-600 tracking-widest font-medium">AI TRADING ASSISTANT</span>
                </div>
                
                {/* Trading system status - kept the time but removed animations */}
                <div className="ml-4 bg-white border border-green-200 px-2 py-1 rounded-md font-mono text-xs text-green-700 hidden md:block">
                  <div className="flex flex-col items-center">
                    <div>{currentTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
                    <div className="text-green-500 text-xs flex items-center">
                      <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                      ONLINE
                    </div>
                  </div>
                </div>
              </Link>
            </div>
            
            {showActions && (
              <div className="flex items-center space-x-4">
                {isLoggedIn ? (
                  <>
                    <button
                      onClick={handleSignalPage}
                      className="px-6 py-2 text-green-600 font-medium hover:bg-green-50 rounded-md transition duration-300"
                    >
                      Trading Signals
                    </button>
                    
                    <button
                      onClick={handleLogout}
                      className="px-6 py-2 border border-green-200 rounded-md text-gray-600 hover:border-green-400 hover:text-green-600 transition-colors duration-300"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <button
                    onClick={handleLogin}
                    disabled={isLoading}
                    className="px-6 py-2 rounded-md shadow-md bg-green-600 text-white hover:bg-green-700 transition-all duration-300"
                  >
                    {isLoading ? 'Connecting...' : 'Login'}
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