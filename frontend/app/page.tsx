// app/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
export default function Home() {
  const router = useRouter();
  const [animatedStats, setAnimatedStats] = useState({
    signals: 0,
    successRate: 0,
    avgReturn: 0
  });
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Set the initial visibility for animation
    setIsVisible(true);
    
    // Animate the stats over time
    const interval = setInterval(() => {
      setAnimatedStats(prev => ({
        signals: prev.signals < 12 ? prev.signals + 1 : 12,
        successRate: prev.successRate < 78 ? prev.successRate + 2 : 78,
        avgReturn: prev.avgReturn < 1.4 ? prev.avgReturn + 0.1 : 1.4
      }));
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const handleLogin = () => {
    router.push('/login');
  };

  const handleSignalPage = () => {
    router.push('/selection');
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Header />

      <main className="flex-grow">
        {/* Hero Section */}
        <section className="pt-16 pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
          <div 
            className={`grid grid-cols-1 gap-12 items-center transition-opacity duration-1000 ${
              isVisible ? 'opacity-100' : 'opacity-0'
            }`}
          >
            <div className="text-center max-w-3xl mx-auto">
              <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
                <span className="block">AI-Powered</span>
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-green-500 to-green-700">
                  Trading Signals
                </span>
              </h1>
              <p className="mt-6 text-lg text-gray-600 max-w-2xl mx-auto">
                Sambot uses advanced AI to analyze market data and generate high-probability
                trading signals for NIFTY and BANKNIFTY, optimized for scalping, swing, and
                long-term trading strategies.
              </p>
              
              {/* Centralized buttons */}
              <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={handleLogin}
                  className="px-8 py-3 rounded-md shadow-lg bg-gradient-to-r from-green-500 to-green-600 text-white hover:from-green-600 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transform hover:-translate-y-1 transition-all duration-300"
                >
                  Login
                </button>
                <button
                  onClick={handleSignalPage}
                  className="px-8 py-3 rounded-md shadow-lg bg-white border-2 border-green-500 text-green-600 hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transform hover:-translate-y-1 transition-all duration-300"
                >
                  Trading Signals
                </button>
              </div>
            </div>
            
            <div className="rounded-xl bg-white shadow-xl overflow-hidden border border-green-100 transform hover:scale-105 transition-transform duration-500 max-w-4xl mx-auto w-full">
              <div className="h-72 bg-gradient-to-r from-green-50 to-green-100 flex items-center justify-center">
                <div className="relative w-full h-full overflow-hidden">
                  {/* Trading chart visualization */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <div className="w-3/4 h-40 relative">
                      {/* Chart line */}
                      <svg viewBox="0 0 100 40" className="w-full h-full">
                        <path 
                          d="M0,20 Q10,15 20,25 T40,15 T60,20 T80,10 T100,15" 
                          fill="none" 
                          stroke="#16A34A" 
                          strokeWidth="1.5"
                          className="animate-draw"
                          strokeDasharray="200"
                          strokeDashoffset="200"
                          style={{
                            animation: 'draw 3s forwards'
                          }}
                        />
                        
                        {/* Candlesticks */}
                        {[10, 25, 40, 55, 70, 85].map((x, i) => (
                          <g key={i} className="animate-fadeIn" style={{ animationDelay: `${i * 0.2}s` }}>
                            <line 
                              x1={x} y1={10 + (i % 3) * 5} 
                              x2={x} y2={25 - (i % 4) * 2} 
                              stroke={i % 2 ? "#16A34A" : "#DC2626"} 
                              strokeWidth="2" 
                            />
                            <rect 
                              x={x - 1.5} 
                              y={15 + (i % 2) * 5} 
                              width="3" 
                              height="6" 
                              fill={i % 2 ? "#16A34A" : "#DC2626"} 
                            />
                          </g>
                        ))}
                      </svg>
                      
                      {/* Buy/Sell indicators */}
                      <div className="absolute top-10 left-1/4 bg-green-500 text-white text-xs px-2 py-1 rounded shadow-md animate-bounce">
                        BUY
                      </div>
                      <div className="absolute bottom-10 right-1/4 bg-red-500 text-white text-xs px-2 py-1 rounded shadow-md animate-bounce" style={{ animationDelay: '1s' }}>
                        SELL
                      </div>
                    </div>
                    <p className="text-gray-600 mt-4">Personal Trading Assistant</p>
                  </div>
                </div>
              </div>
              
              <div className="px-6 py-4">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <div className="text-xs text-gray-500">Today's Signals</div>
                    <div className="font-bold text-2xl text-green-800">{animatedStats.signals}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">Success Rate</div>
                    <div className="font-bold text-2xl text-green-600">{animatedStats.successRate}%</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">Avg. Return</div>
                    <div className="font-bold text-2xl text-green-600">+{animatedStats.avgReturn.toFixed(1)}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 bg-gradient-to-b from-white to-green-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
              <span className="inline-block relative">
                Key Features
                <span className="absolute bottom-0 left-0 w-full h-1 bg-green-400"></span>
              </span>
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  icon: '🎯',
                  title: 'Precision Signals',
                  description: 'Highly accurate trading signals based on multiple technical indicators and pattern recognition.'
                },
                {
                  icon: '⚡',
                  title: 'Real-time Execution',
                  description: 'Automated trade execution with customizable risk management rules.'
                },
                {
                  icon: '🧠',
                  title: 'Adaptive AI',
                  description: 'Our AI continually learns from market conditions to improve signal quality.'
                }
              ].map((feature, index) => (
                <div 
                  key={index}
                  className="bg-white p-6 rounded-xl shadow-md hover:shadow-xl border border-green-100 transform hover:-translate-y-2 transition-all duration-300"
                >
                  <div className="text-4xl mb-4 bg-green-100 w-16 h-16 rounded-full flex items-center justify-center text-green-800">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-medium text-green-800">{feature.title}</h3>
                  <p className="mt-2 text-gray-600">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>

            {/* Second row of features */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
              {[
                {
                  icon: '📊',
                  title: 'Multi-Timeframe Analysis',
                  description: 'Analyze markets across multiple timeframes from 1-minute charts to daily charts for comprehensive insights.'
                },
                {
                  icon: '🔔',
                  title: 'Custom Alerts',
                  description: 'Get notified instantly when high-probability setups form with customizable alert settings.'
                }
              ].map((feature, index) => (
                <div 
                  key={index}
                  className="bg-white p-6 rounded-xl shadow-md hover:shadow-xl border border-green-100 transform hover:-translate-y-2 transition-all duration-300"
                >
                  <div className="text-4xl mb-4 bg-green-100 w-16 h-16 rounded-full flex items-center justify-center text-green-800">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-medium text-green-800">{feature.title}</h3>
                  <p className="mt-2 text-gray-600">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
            
            {/* Action buttons centered below features */}
            <div className="mt-16 flex justify-center">
              <button
                onClick={handleSignalPage}
                className="px-8 py-3 rounded-md shadow-lg bg-gradient-to-r from-green-500 to-green-600 text-white hover:from-green-600 hover:to-green-700 transform hover:scale-105 transition-all duration-300 mx-4"
              >
                Get Started Now
              </button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
      
      {/* Add styles for the animations */}
      <style jsx>{`
        @keyframes draw {
          to {
            stroke-dashoffset: 0;
          }
        }
        
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        
        .animate-draw {
          animation: draw 3s forwards;
        }
        
        .animate-fadeIn {
          opacity: 0;
          animation: fadeIn 1s forwards;
        }
      `}</style>
    </div>
  );
}