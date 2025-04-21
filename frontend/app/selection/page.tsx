// app/selection/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import UploadPDF from '@/components/UploadPDF'


// Define types for our component props and state
type IndexType = 'NIFTY' | 'BANKNIFTY';
type ModeType = 'scalp' | 'swing' | 'longterm';

interface FormData {
  indexes: IndexType[];
  modes: ModeType[];
  auto_execute: boolean;
}

// Mock function for API call since the actual implementation might not be available
const submitTradingPreference = async (data: FormData) => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const signals = [];
  
  // Generate demo signals for each selected index and mode combination
  for (const index of data.indexes) {
    for (const mode of data.modes) {
      signals.push({
        id: `${index}-${mode}-${Date.now()}`,
        symbol: index,
        action: Math.random() > 0.5 ? 'BUY' : 'SELL',
        price: index === 'NIFTY' ? 22450.75 : 48750.25,
        target_price: index === 'NIFTY' ? 22500.00 : 48850.00,
        stop_loss: index === 'NIFTY' ? 22400.00 : 48650.00,
        quantity: index === 'NIFTY' ? 50 : 25,
        potential_return: 0.0022,
        risk_reward_ratio: 1.8,
        timeframe: mode === 'scalp' ? '5min' : mode === 'swing' ? '1hour' : '1day',
        confidence_score: 70 + Math.floor(Math.random() * 20),
        indicators: ['RSI', 'MACD', 'VWAP', 'Bollinger Bands'],
        patterns: ['Support/Resistance', 'Trend Line'],
        notes: `${index} ${mode} opportunity with strong confirmation`,
        timestamp: new Date().toISOString(),
        executed: false
      });
    }
  }
  
  return {
    executed_signals: [],
    non_executed_signals: signals
  };
};

export default function SelectionPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<FormData>({
    indexes: ['NIFTY'],
    modes: ['scalp'],
    auto_execute: false
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is authenticated when component mounts
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
      } else {
        setIsAuthenticated(true);
      }
    };
    
    // We need to use setTimeout because localStorage is not available during SSR
    const timer = setTimeout(() => {
      checkAuth();
    }, 0);
    
    return () => clearTimeout(timer);
  }, [router]);

  const handleIndexToggle = (index: IndexType) => {
    setFormData(prev => {
      // If already selected, remove it
      if (prev.indexes.includes(index)) {
        // Don't allow deselecting the last item
        if (prev.indexes.length === 1) {
          return prev;
        }
        return {
          ...prev,
          indexes: prev.indexes.filter(i => i !== index)
        };
      } 
      // Otherwise add it
      return {
        ...prev,
        indexes: [...prev.indexes, index]
      };
    });
  };

  const handleModeToggle = (mode: ModeType) => {
    setFormData(prev => {
      // If already selected, remove it
      if (prev.modes.includes(mode)) {
        // Don't allow deselecting the last item
        if (prev.modes.length === 1) {
          return prev;
        }
        return {
          ...prev,
          modes: prev.modes.filter(m => m !== mode)
        };
      } 
      // Otherwise add it
      return {
        ...prev,
        modes: [...prev.modes, mode]
      };
    });
  };

  const handleAutoExecuteChange = (auto_execute: boolean) => {
    setFormData(prev => ({ ...prev, auto_execute }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const response = await submitTradingPreference(formData);
      // Store response in localStorage for the signals page
      localStorage.setItem('tradingSignals', JSON.stringify(response));
      router.push('/signals');
    } catch (error) {
      console.error('Error submitting preferences:', error);
      // Show error notification
    } finally {
      setIsSubmitting(false);
    }
  };

  // Show loading state until we've checked authentication
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-white to-green-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Header showActions={false} />

      <main className="flex-grow bg-gradient-to-br from-white to-green-50">
        <div className="max-w-lg mx-auto px-4 py-12">
          <div className="bg-white shadow rounded-lg overflow-hidden border border-green-100">
            <div className="px-6 py-8">
              <h1 className="text-2xl font-bold text-gray-900 text-center mb-8">
                Configure Trading Mode
              </h1>
              <form onSubmit={handleSubmit} className="space-y-8">
                {/* Index Selection */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <label className="block text-sm font-medium text-gray-700">
                      Choose Index
                    </label>
                    <span className="text-xs text-gray-500">
                      {formData.indexes.length} selected
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <button
                      type="button"
                      className={`p-4 rounded-lg border-2 flex items-center justify-center ${
                        formData.indexes.includes('NIFTY')
                          ? 'border-green-500 bg-green-50 text-green-700'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                      onClick={() => handleIndexToggle('NIFTY')}
                    >
                      <span className="font-medium">NIFTY</span>
                    </button>
                    <button
                      type="button"
                      className={`p-4 rounded-lg border-2 flex items-center justify-center ${
                        formData.indexes.includes('BANKNIFTY')
                          ? 'border-green-500 bg-green-50 text-green-700'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                      onClick={() => handleIndexToggle('BANKNIFTY')}
                    >
                      <span className="font-medium">BANKNIFTY</span>
                    </button>
                  </div>
                </div>

                {/* Trading Mode Selection */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <label className="block text-sm font-medium text-gray-700">
                      Choose Trading Mode
                    </label>
                    <span className="text-xs text-gray-500">
                      {formData.modes.length} selected
                    </span>
                  </div>
                  <div className="space-y-2">
                    <button
                      type="button"
                      className={`w-full p-3 rounded-lg border flex items-center ${
                        formData.modes.includes('scalp')
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                      onClick={() => handleModeToggle('scalp')}
                    >
                      <span className="text-xl mr-3">🐇</span>
                      <div className="text-left">
                        <div className="font-medium">Scalping</div>
                        <div className="text-xs text-gray-500">Short-term trades (minutes to hours)</div>
                      </div>
                      {formData.modes.includes('scalp') && (
                        <div className="ml-auto bg-green-100 rounded-full p-1">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </button>
                    
                    <button
                      type="button"
                      className={`w-full p-3 rounded-lg border flex items-center ${
                        formData.modes.includes('swing')
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                      onClick={() => handleModeToggle('swing')}
                    >
                      <span className="text-xl mr-3">🐢</span>
                      <div className="text-left">
                        <div className="font-medium">Swing</div>
                        <div className="text-xs text-gray-500">Medium-term trades (days to weeks)</div>
                      </div>
                      {formData.modes.includes('swing') && (
                        <div className="ml-auto bg-green-100 rounded-full p-1">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </button>
                    
                    <button
                      type="button"
                      className={`w-full p-3 rounded-lg border flex items-center ${
                        formData.modes.includes('longterm')
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200 hover:bg-gray-50'
                      }`}
                      onClick={() => handleModeToggle('longterm')}
                    >
                      <span className="text-xl mr-3">🧘</span>
                      <div className="text-left">
                        <div className="font-medium">Long-term</div>
                        <div className="text-xs text-gray-500">Strategic investments (months+)</div>
                      </div>
                      {formData.modes.includes('longterm') && (
                        <div className="ml-auto bg-green-100 rounded-full p-1">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </button>
                  </div>
                </div>

                {/* Selected Combinations */}
                <div className="bg-green-50 p-3 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Selected Combinations</h3>
                  <div className="flex flex-wrap gap-2">
                    {formData.indexes.flatMap(index => 
                      formData.modes.map(mode => (
                        <div 
                          key={`${index}-${mode}`} 
                          className="bg-white px-2 py-1 text-xs rounded border border-green-200 shadow-sm"
                        >
                          {index} + {mode === 'scalp' ? '🐇' : mode === 'swing' ? '🐢' : '🧘'}
                        </div>
                      ))
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    {formData.indexes.length * formData.modes.length} trading combinations selected
                  </p>
                </div>

                {/* Auto-Execute Toggle */}
                <div className="flex items-center justify-between py-2">
                  <div>
                    <h3 className="text-sm font-medium text-gray-700">Auto Order Execution</h3>
                    <p className="text-xs text-gray-500">Automatically place trades based on signals</p>
                  </div>
                  <button
                    type="button"
                    className={`
                      relative inline-flex h-6 w-11 items-center rounded-full
                      ${formData.auto_execute ? 'bg-green-600' : 'bg-gray-200'}
                    `}
                    onClick={() => handleAutoExecuteChange(!formData.auto_execute)}
                  >
                    <span
                      className={`
                        inline-block h-4 w-4 transform rounded-full bg-white transition
                        ${formData.auto_execute ? 'translate-x-6' : 'translate-x-1'}
                      `}
                    />
                  </button>
                </div>
                <UploadPDF />

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={`w-full py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${
                    isSubmitting ? 'opacity-75 cursor-not-allowed' : ''
                  }`}
                >
                  {isSubmitting ? 'Processing...' : `Get Trading Signals (${formData.indexes.length * formData.modes.length})`}
                </button>
              </form>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}