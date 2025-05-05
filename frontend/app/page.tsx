// app/page.tsx
'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';

export default function Home() {
  const router = useRouter();
  const canvasRef = useRef(null);
  const [animatedStats, setAnimatedStats] = useState({
    signals: 0,
    successRate: 0,
    avgReturn: 0,
    activeTraders: 0
  });
  const [isVisible, setIsVisible] = useState(false);
  const [currentTestimonial, setCurrentTestimonial] = useState(0);

  useEffect(() => {
    // Set the initial visibility for animation
    setIsVisible(true);
    
    // Animate the stats over time
    const interval = setInterval(() => {
      setAnimatedStats(prev => ({
        signals: prev.signals < 15 ? prev.signals + 1 : 15,
        successRate: prev.successRate < 87 ? prev.successRate + 2 : 87,
        avgReturn: prev.avgReturn < 2.8 ? prev.avgReturn + 0.2 : 2.8,
        activeTraders: prev.activeTraders < 1250 ? prev.activeTraders + 50 : 1250
      }));
    }, 100);

    // Rotate testimonials
    const testimonialInterval = setInterval(() => {
      setCurrentTestimonial(prev => (prev + 1) % 3);
    }, 5000);

    // Initialize floating elements animation
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      const particles = [];
      const particleCount = 50;

      // Set canvas size
      const resizeCanvas = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      };
      
      resizeCanvas();
      window.addEventListener('resize', resizeCanvas);

      // Create particles
      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          radius: Math.random() * 5 + 2,
          speedX: Math.random() * 1 - 0.5,
          speedY: Math.random() * 1 - 0.5,
          color: `rgba(0, 128, 0, ${Math.random() * 0.2 + 0.1})`
        });
      }

      // Animation function
      const animate = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw and update particles
        particles.forEach(particle => {
          ctx.beginPath();
          ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
          ctx.fillStyle = particle.color;
          ctx.fill();
          
          // Update position
          particle.x += particle.speedX;
          particle.y += particle.speedY;
          
          // Wrap around edges
          if (particle.x < 0 || particle.x > canvas.width) particle.speedX *= -1;
          if (particle.y < 0 || particle.y > canvas.height) particle.speedY *= -1;
          
          // Connect particles with lines if they're close enough
          particles.forEach(otherParticle => {
            const dx = particle.x - otherParticle.x;
            const dy = particle.y - otherParticle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < 150) {
              ctx.beginPath();
              ctx.strokeStyle = `rgba(0, 128, 0, ${0.1 - distance/1500})`;
              ctx.lineWidth = 0.5;
              ctx.moveTo(particle.x, particle.y);
              ctx.lineTo(otherParticle.x, otherParticle.y);
              ctx.stroke();
            }
          });
        });
        
        requestAnimationFrame(animate);
      };
      
      animate();
      
      return () => {
        clearInterval(interval);
        clearInterval(testimonialInterval);
        window.removeEventListener('resize', resizeCanvas);
      };
    }
    
    return () => {
      clearInterval(interval);
      clearInterval(testimonialInterval);
    };
  }, []);

  const handleLogin = () => {
    router.push('/login');
  };

  const handleSignalPage = () => {
    router.push('/selection');
  };

  const handleMarketInsights = () => {
    router.push('/insights');
  };

  const testimonials = [
    {
      name: "Rahul Sharma",
      role: "Day Trader",
      image: "/assets/testimonial1.jpg",
      text: "Samurai's precision signals have transformed my trading routine. I've increased my success rate by 36% in just 3 months."
    },
    {
      name: "Priya Patel",
      role: "Swing Trader",
      image: "/assets/testimonial2.jpg",
      text: "The market insight reports are incredibly valuable. I can now anticipate market movements with far greater accuracy than before."
    },
    {
      name: "Vikram Mehra",
      role: "Options Trader",
      image: "/assets/testimonial3.jpg",
      text: "The AI's ability to detect pattern formations before they complete has given me a critical edge in options trading."
    }
  ];

  const features = [
    {
      icon: '📊',
      title: 'Smart NIFTY Analysis',
      description: 'Real-time analysis of NIFTY and BANKNIFTY with predictive modeling that identifies high-probability trading zones before they form.',
      color: 'from-green-400 to-emerald-500'
    },
    {
      icon: '⚡',
      title: 'Trend Accelerator',
      description: 'Advanced algorithm that detects the earliest signs of trend changes, giving you entry signals before the big moves happen.',
      color: 'from-emerald-400 to-teal-500'
    },
    {
      icon: '🧠',
      title: 'Learning Engine',
      description: 'Self-improving AI that continuously analyzes market patterns and adjusts its strategy to maintain peak performance in all market conditions.',
      color: 'from-teal-400 to-cyan-500'
    },
    {
      icon: '🎯',
      title: 'Risk Calculator',
      description: 'Custom risk management tools that automatically suggest optimal position sizes and stop-loss levels based on your trading style.',
      color: 'from-cyan-400 to-blue-500'
    },
    {
      icon: '🔔',
      title: 'Priority Alerts',
      description: 'Instant notifications with detailed trade setups delivered straight to your phone or desktop in real-time.',
      color: 'from-blue-400 to-indigo-500'
    },
    {
      icon: '📱',
      title: 'Mobile Trading Suite',
      description: 'Complete trading environment accessible from any device, letting you manage positions and receive signals anywhere.',
      color: 'from-indigo-400 to-violet-500'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white flex flex-col relative overflow-hidden">
      <canvas ref={canvasRef} className="absolute inset-0 z-0" />
      
      <Header />

      <main className="flex-grow z-10">
        {/* Hero Section */}
        <section className="pt-16 pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto relative">
          <div 
            className={`grid md:grid-cols-2 gap-12 items-center transition-all duration-1000 ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
            }`}
          >
            <div className="text-center md:text-left max-w-lg mx-auto md:mx-0">
              <div className="hidden md:block absolute -top-10 -left-10 w-72 h-72 bg-green-300 rounded-full mix-blend-multiply filter blur-5xl opacity-30 animate-blob"></div>
              <div className="hidden md:block absolute top-60 -right-20 w-72 h-72 bg-cyan-300 rounded-full mix-blend-multiply filter blur-5xl opacity-30 animate-blob animation-delay-2000"></div>
              
              <div className="inline-flex items-center bg-green-100 rounded-full px-4 py-1 text-green-800 mb-6">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M5 2a1 1 0 011 1v1h1a1 1 0 010 2H6v1a1 1 0 01-2 0V6H3a1 1 0 010-2h1V3a1 1 0 011-1zm0 10a1 1 0 011 1v1h1a1 1 0 110 2H6v1a1 1 0 11-2 0v-1H3a1 1 0 110-2h1v-1a1 1 0 011-1zm7-10a1 1 0 01.707.293l.707.707.707-.707A1 1 0 0116 3v1h1a1 1 0 110 2h-1v1a1 1 0 11-2 0V6h-1a1 1 0 110-2h1V3a1 1 0 011-1zm0 10a1 1 0 01.707.293l.707.707.707-.707A1 1 0 0116 13v1h1a1 1 0 110 2h-1v1a1 1 0 11-2 0v-1h-1a1 1 0 110-2h1v-1a1 1 0 011-1z" clipRule="evenodd"></path>
                </svg>
                <span className="text-sm font-medium">NEW: Market Sentiment Analysis</span>
              </div>
              
              <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
                <span className="block">Trade smarter with</span>
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-teal-500 animate-gradient">
                  Samurai
                </span>
              </h1>
              <p className="mt-4 text-lg text-gray-600 max-w-xl">
                Harness the power of next-gen artificial intelligence to unlock profitable trading opportunities in NIFTY and BANKNIFTY with precision signals, real-time analytics, and adaptive strategies.
              </p>
              
              {/* Stat counters */}
              <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-white rounded-lg shadow-sm p-4 border border-green-100">
                  <p className="text-sm text-gray-500">Daily Signals</p>
                  <p className="text-2xl font-bold text-green-600">{animatedStats.signals}</p>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-4 border border-green-100">
                  <p className="text-sm text-gray-500">Success Rate</p>
                  <p className="text-2xl font-bold text-green-600">{animatedStats.successRate}%</p>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-4 border border-green-100">
                  <p className="text-sm text-gray-500">Avg. Return</p>
                  <p className="text-2xl font-bold text-green-600">+{animatedStats.avgReturn.toFixed(1)}%</p>
                </div>
                <div className="bg-white rounded-lg shadow-sm p-4 border border-green-100">
                  <p className="text-sm text-gray-500">Active Traders</p>
                  <p className="text-2xl font-bold text-green-600">{animatedStats.activeTraders.toLocaleString()}</p>
                </div>
              </div>
              
              {/* CTA buttons */}
              <div className="mt-8 flex flex-col sm:flex-row gap-4 md:justify-start justify-center">
                <button
                  onClick={handleSignalPage}
                  className="px-6 py-3 rounded-lg shadow-lg bg-gradient-to-r from-green-500 to-teal-500 text-white font-medium hover:from-green-600 hover:to-teal-600 transform hover:scale-105 transition-all duration-300"
                >
                  Get Trading Signals
                </button>
                <button
                  onClick={handleMarketInsights}
                  className="px-6 py-3 rounded-lg shadow-lg bg-white border border-green-500 text-green-600 font-medium hover:bg-green-50 transform hover:scale-105 transition-all duration-300"
                >
                  Market Insights
                </button>
              </div>
            </div>
            
            <div className="relative">
              {/* Animated trading interface */}
              <div className="relative rounded-2xl shadow-xl overflow-hidden border border-green-200 bg-white transform hover:scale-102 transition-transform duration-500 max-w-lg mx-auto">
                {/* Interface header */}
                <div className="bg-gradient-to-r from-green-600 to-teal-500 px-4 py-3 flex justify-between items-center">
                  <div className="flex items-center">
                    <div className="h-3 w-3 rounded-full bg-red-400 mr-2"></div>
                    <div className="h-3 w-3 rounded-full bg-yellow-400 mr-2"></div>
                    <div className="h-3 w-3 rounded-full bg-green-400"></div>
                  </div>
                  <div className="text-white text-sm font-medium">Samurai Trading Dashboard</div>
                  <div className="text-white text-xs opacity-70">LIVE</div>
                </div>
                
                {/* Trading chart */}
                <div className="h-64 bg-white relative">
                  {/* Chart grid lines */}
                  <div className="absolute inset-0 grid grid-cols-6 grid-rows-4">
                    {Array(24).fill(0).map((_, i) => (
                      <div key={i} className="border-r border-t border-gray-100"></div>
                    ))}
                  </div>
                  
                  {/* Chart visualization */}
                  <svg viewBox="0 0 100 40" className="w-full h-full relative z-10">
                    <defs>
                      <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="rgba(16, 185, 129, 0.2)" />
                        <stop offset="100%" stopColor="rgba(16, 185, 129, 0)" />
                      </linearGradient>
                    </defs>
                    
                    {/* Area under chart */}
                    <path 
                      d="M0,22 Q10,20 20,18 T30,15 T40,25 T50,22 T60,13 T70,20 T80,15 T90,18 T100,15 V40 H0 Z" 
                      fill="url(#chartGradient)"
                    />
                    
                    {/* Chart line */}
                    <path 
                      d="M0,22 Q10,20 20,18 T30,15 T40,25 T50,22 T60,13 T70,20 T80,15 T90,18 T100,15" 
                      fill="none" 
                      stroke="#10B981" 
                      strokeWidth="1.5"
                      className="animate-draw"
                      strokeDasharray="200"
                      strokeDashoffset="200"
                    />
                    
                    {/* Data points */}
                    {[
                      {x: 0, y: 22},
                      {x: 20, y: 18},
                      {x: 30, y: 15},
                      {x: 40, y: 25},
                      {x: 50, y: 22},
                      {x: 60, y: 13},
                      {x: 70, y: 20},
                      {x: 80, y: 15},
                      {x: 90, y: 18},
                      {x: 100, y: 15}
                    ].map((point, i) => (
                      <g key={i} className="animate-fadeIn" style={{ animationDelay: `${i * 0.1}s` }}>
                        <circle 
                          cx={point.x} 
                          cy={point.y} 
                          r="1.2" 
                          fill="#10B981" 
                        />
                      </g>
                    ))}
                    
                    {/* Buy indicator */}
                    <g className="animate-fadeIn" style={{ animationDelay: `0.8s` }}>
                      <circle cx="40" cy="25" r="2.5" fill="rgba(16, 185, 129, 0.3)" />
                      <circle cx="40" cy="25" r="1.5" fill="#10B981" />
                      <line x1="40" y1="25" x2="40" y2="35" stroke="#10B981" strokeWidth="0.5" strokeDasharray="2,1" />
                      <text x="40" y="38" fontSize="3" fill="#10B981" textAnchor="middle">BUY</text>
                    </g>
                    
                    {/* Sell indicator */}
                    <g className="animate-fadeIn" style={{ animationDelay: `1.2s` }}>
                      <circle cx="60" cy="13" r="2.5" fill="rgba(239, 68, 68, 0.3)" />
                      <circle cx="60" cy="13" r="1.5" fill="#EF4444" />
                      <line x1="60" y1="13" x2="60" y2="5" stroke="#EF4444" strokeWidth="0.5" strokeDasharray="2,1" />
                      <text x="60" y="3" fontSize="3" fill="#EF4444" textAnchor="middle">SELL</text>
                    </g>
                  </svg>
                  
                  {/* Signal overlay */}
                  <div className="absolute top-4 right-4 bg-green-50 border border-green-200 rounded-lg p-2 shadow-sm animate-pulse-slow">
                    <div className="text-xs text-green-800 font-medium flex items-center space-x-1">
                      <span className="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
                      <span>NIFTY: LONG @ 19845</span>
                    </div>
                  </div>
                </div>
                
                {/* Dashboard details */}
                <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
                  <div className="grid grid-cols-3 gap-2">
                    <div className="bg-white p-2 rounded shadow-sm">
                      <div className="text-xs text-gray-500">Signal Strength</div>
                      <div className="font-medium text-green-600">
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '85%' }}></div>
                        </div>
                      </div>
                    </div>
                    <div className="bg-white p-2 rounded shadow-sm">
                      <div className="text-xs text-gray-500">Stop Loss</div>
                      <div className="font-medium text-red-600">19780</div>
                    </div>
                    <div className="bg-white p-2 rounded shadow-sm">
                      <div className="text-xs text-gray-500">Target</div>
                      <div className="font-medium text-green-600">19950</div>
                    </div>
                  </div>
                </div>
                
                {/* Trading actions */}
                <div className="px-4 py-3 border-t border-gray-100 flex justify-between">
                  <button className="bg-green-500 text-white text-sm font-medium px-4 py-1 rounded">Buy Now</button>
                  <button className="bg-gray-100 text-gray-700 text-sm font-medium px-4 py-1 rounded">Set Alert</button>
                  <button className="bg-gray-100 text-gray-700 text-sm font-medium px-4 py-1 rounded">Details</button>
                </div>
              </div>
              
              {/* Mobile notification overlay */}
              <div className="absolute -bottom-6 -right-6 w-44 bg-white rounded-lg shadow-lg border border-green-100 p-3 transform rotate-6 animate-float">
                <div className="flex items-start space-x-2">
                  <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center text-white">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                    </svg>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-900">Samurai Signal</p>
                    <p className="text-xs text-gray-600">BankNifty: Buy at 46350</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Testimonial Section */}
        <section className="py-12 bg-green-50 relative overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
              <span className="inline-block relative">
                What Our Traders Say
                <span className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-green-400 to-teal-500"></span>
              </span>
            </h2>
            
            <div className="relative h-64">
              {testimonials.map((testimonial, index) => (
                <div
                  key={index}
                  className={`absolute inset-0 transition-all duration-500 flex items-center justify-center ${
                    index === currentTestimonial 
                      ? 'opacity-100 translate-x-0' 
                      : index < currentTestimonial 
                        ? 'opacity-0 -translate-x-full' 
                        : 'opacity-0 translate-x-full'
                  }`}
                >
                  <div className="bg-white rounded-xl shadow-lg p-8 max-w-2xl mx-auto">
                    <div className="flex flex-col md:flex-row gap-6 items-center">
                      <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                        <div className="text-2xl text-green-700">{testimonial.name.charAt(0)}</div>
                      </div>
                      <div className="text-center md:text-left">
                        <p className="text-gray-600 italic mb-4">"{testimonial.text}"</p>
                        <p className="font-medium text-gray-900">{testimonial.name}</p>
                        <p className="text-sm text-gray-500">{testimonial.role}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Pagination dots */}
              <div className="absolute bottom-0 left-0 right-0 flex justify-center space-x-2">
                {testimonials.map((_, index) => (
                  <button
                    key={index}
                    className={`w-2 h-2 rounded-full ${
                      index === currentTestimonial ? 'bg-green-500' : 'bg-gray-300'
                    }`}
                    onClick={() => setCurrentTestimonial(index)}
                  />
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
              <span className="inline-block relative">
                Intelligent Trading Features
                <span className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-green-400 to-teal-500"></span>
              </span>
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {features.map((feature, index) => (
                <div 
                  key={index}
                  className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 hover:shadow-lg hover:border-green-200 transition-all duration-300 transform hover:-translate-y-1"
                >
                  <div className={`h-2 bg-gradient-to-r ${feature.color}`}></div>
                  <div className="p-6">
                    <div className={`text-4xl mb-4 w-14 h-14 rounded-lg bg-gradient-to-r ${feature.color} bg-opacity-10 flex items-center justify-center text-transparent bg-clip-text bg-gradient-to-r ${feature.color}`}>
                      {feature.icon}
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                    <p className="text-gray-600">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
        
        {/* How It Works Section */}
        <section className="py-16 bg-gradient-to-b from-white to-green-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
              <span className="inline-block relative">
                How Samurai Works
                <span className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-green-400 to-teal-500"></span>
              </span>
            </h2>
            
            <div className="relative">
              {/* Connecting line */}
              <div className="absolute top-24 left-0 right-0 h-0.5 bg-green-200 z-0 hidden md:block"></div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                {[
                  {
                    icon: '📥',
                    title: 'Data Collection',
                    description: 'Samurai continuously gathers data from multiple market sources, news, and sentiment indicators.'
                  },
                  {
                    icon: '⚙️',
                    title: 'AI Processing',
                    description: 'Our neural networks analyze patterns and correlations across various timeframes and indicators.'
                  },
                  {
                    icon: '🔍',
                    title: 'Signal Generation',
                    description: 'The system generates high-probability trade signals with precise entry, target, and stop-loss levels.'
                  },
                  {
                    icon: '📱',
                    title: 'Instant Delivery',
                    description: 'Trading signals are delivered to your preferred device in real-time with actionable insights.'
                  }
                ].map((step, index) => (
                  <div key={index} className="relative z-10 flex flex-col items-center">
                    <div className="bg-white w-16 h-16 rounded-full border-2 border-green-500 flex items-center justify-center text-2xl shadow-md mb-4">
                      {step.icon}
                    </div>
                    <h3 className="text-xl font-medium text-gray-900 mb-2 text-center">{step.title}</h3>
                    <p className="text-gray-600 text-center">{step.description}</p>
                  </div>
                ))}
              </div>
            </div>
            
            {/* CTA Button */}
            <div className="mt-16 flex justify-center">
              <button
                onClick={handleSignalPage}
                className="group relative px-8 py-4 rounded-lg overflow-hidden border-2 border-green-500 text-green-600 font-medium hover:text-white"
              >
                <span className="absolute top-0 left-0 w-full h-0 bg-green-500 transition-all duration-300 group-hover:h-full"></span>
                <span className="relative flex items-center">
                  <span>Start Trading with Samurai</span>
                  <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                  </svg>
                </span>
              </button>
            </div>
          </div>
        </section>
        
        {/* Market Analysis Section */}
        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-6">
                  <span className="relative inline-block">
                    Market Analysis
                    <span className="absolute -bottom-2 left-0 w-full h-1 bg-gradient-to-r from-green-400 to-teal-500"></span>
                  </span>
                  <span className="text-green-600"> at Your Fingertips</span>
                </h2>
                
                <p className="text-gray-600 mb-6">
                  Samurai doesn't just provide trading signals - it gives you deep market insights that help you understand the 'why' behind every recommendation.
                </p>
                
                <div className="space-y-4">
                  {[
                    'Sector rotation analysis to identify where money is flowing',
                    'Options flow indicators showing institutional positioning',
                    'Fibonacci-based key levels and reversal zones',
                    'Volume profile analysis for support/resistance identification'
                  ].map((item, index) => (
                    <div key={index} className="flex items-start">
                      <div className="flex-shrink-0 h-6 w-6 rounded-full bg-green-100 flex items-center justify-center text-green-600 mr-3">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                        </svg>
                      </div>
                      <p className="text-gray-600">{item}</p>
                    </div>
                  ))}
                </div>
                
                <button
                  onClick={handleMarketInsights}
                  className="mt-8 inline-flex items-center px-6 py-3 rounded-lg shadow-md bg-white border border-green-500 text-green-600 font-medium hover:bg-green-50 transition-all duration-300"
                >
                  <span>Explore Market Insights</span>
                  <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </button>
              </div>
              
              <div className="relative">
                <div className="absolute -top-4 -right-4 w-72 h-72 bg-green-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
                
                <div className="relative grid grid-cols-2 gap-4">
                  <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">NIFTY Heatmap</h4>
                    <div className="grid grid-cols-5 gap-1 p-1 bg-gray-50 rounded">
                      {Array(25).fill(0).map((_, i) => (
                        <div 
                          key={i} 
                          className={`rounded aspect-square ${
                            i % 3 === 0 ? 'bg-green-500' : 
                            i % 5 === 0 ? 'bg-red-500' : 
                            i % 7 === 0 ? 'bg-yellow-500' : 
                            'bg-green-200'
                          }`}
                        ></div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Options Chain</h4>
                    <div className="space-y-2">
                      {[
                        { strike: '19750 PE', oi: '65%', color: 'bg-red-500' },
                        { strike: '19800 PE', oi: '48%', color: 'bg-red-400' },
                        { strike: '19850 CE', oi: '52%', color: 'bg-green-400' },
                        { strike: '19900 CE', oi: '78%', color: 'bg-green-500' }
                      ].map((item, i) => (
                        <div key={i} className="flex justify-between items-center text-xs">
                          <span className="text-gray-700">{item.strike}</span>
                          <div className="w-3/5 bg-gray-100 rounded-full h-2">
                            <div className={`${item.color} h-2 rounded-full`} style={{ width: item.oi }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-100 col-span-2">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Market Sentiment</h4>
                    <div className="flex items-center justify-between">
                      <div className="text-red-500 font-medium">Bearish</div>
                      <div className="w-3/5 bg-gray-100 rounded-full h-2.5">
                        <div className="bg-gradient-to-r from-red-500 via-yellow-400 to-green-500 h-2.5 rounded-full" style={{ width: '65%' }}></div>
                      </div>
                      <div className="text-green-500 font-medium">Bullish</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        {/* Join Now Banner */}
        <section className="bg-gradient-to-r from-green-600 to-teal-500 py-12 text-white">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to transform your trading?</h2>
            <p className="text-green-100 mb-8 max-w-3xl mx-auto">
              Join thousands of traders who are already leveraging Samurai for consistent profits and reduced stress.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={handleSignalPage}
                className="px-8 py-3 rounded-lg shadow-lg bg-white text-green-600 font-medium hover:bg-green-50 transform hover:scale-105 transition-all duration-300"
              >
                Get Started Now
              </button>
              <button
                onClick={handleLogin}
                className="px-8 py-3 rounded-lg shadow-lg bg-green-700 bg-opacity-30 text-white border border-white border-opacity-30 font-medium hover:bg-opacity-40 transform hover:scale-105 transition-all duration-300"
              >
                Learn More
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
        
        @keyframes pulse-slow {
          0%, 100% {
            opacity: 0.7;
          }
          50% {
            opacity: 1;
          }
        }
        
        @keyframes float {
          0% {
            transform: translateY(0px) rotate(6deg);
          }
          50% {
            transform: translateY(-10px) rotate(6deg);
          }
          100% {
            transform: translateY(0px) rotate(6deg);
          }
        }
        
        @keyframes gradient {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }
        
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(20px, -20px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        
        .animate-draw {
          animation: draw 3s forwards;
        }
        
        .animate-fadeIn {
          opacity: 0;
          animation: fadeIn 1s forwards;
        }
        
        .animate-pulse-slow {
          animation: pulse-slow 3s infinite;
        }
        
        .animate-float {
          animation: float 4s ease-in-out infinite;
        }
        
        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 3s ease infinite;
        }
        
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        
        .animate-blob {
          animation: blob 7s infinite;
        }
        
        .hover:scale-102:hover {
          transform: scale(1.02);
        }
      `}</style>
    </div>
  );
o