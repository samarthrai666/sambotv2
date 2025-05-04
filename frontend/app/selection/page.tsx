'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import UploadPDF from '@/components/UploadPDF';
import OptionsTrading from '@/components/trading/OptionsTrading';
import SwingEquityTrading from '@/components/trading/SwingEquityTrading';
import IntradayEquityTrading from '@/components/trading/IntradayEquityTrading';

// Define types for our component props and state
type IndexType = 'NIFTY' | 'BANKNIFTY';
type ModeType = 'scalp' | 'swing' | 'longterm';
type EquitySwingMode = 'momentum' | 'breakout' | 'reversal';
type EquityIntradayMode = 'opening_range' | 'trend_following' | 'mean_reversion';
type SectorType = 'IT' | 'Banking' | 'Auto' | 'Pharma' | 'FMCG';
type Timeframe = '1m' | '5m' | '15m' | '1h';
type RiskLevel = '0.5' | '1.0' | '1.5' | '2.0';
type ScanFrequency = 'daily' | 'weekly' | 'monthly';
type MarketCapType = 'largecap' | 'midcap' | 'smallcap';

// Interface for SwingEquityData
interface SwingEquityData {
  enabled: boolean;
  modes: EquitySwingMode[];
  max_stocks: number;
  sectors: SectorType[];
  scan_frequency: ScanFrequency;
  market_caps: MarketCapType[];
}

// Interface for IntradayEquityData
interface IntradayEquityData {
  enabled: boolean;
  modes: EquityIntradayMode[];
  max_stocks: number;
  timeframes: Timeframe[];
  risk_per_trade: RiskLevel;
  sectors: SectorType[];
  stock_universe: string[];
  smart_filter: boolean;
}

// Interface for OptionsData
interface OptionsData {
  enabled: boolean;
  indexes: IndexType[];
  modes: ModeType[];
  auto_execute: boolean;
}

interface FormData {
  // Options trading
  options: OptionsData;
  
  // Intraday Trading
  intraday: {
    enabled: boolean;
    equity: IntradayEquityData;
  };
  
  // Equity Trading
  equity: {
    enabled: boolean;
    swing: SwingEquityData;
  };
}

export default function SelectionPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // Define the form data with initializing from previously saved data when available
  const [formData, setFormData] = useState<FormData>({
    options: {
      enabled: false,
      indexes: [],
      modes: [],
      auto_execute: false,
    },
    intraday: {
      enabled: false,
      equity: {
        enabled: false,
        modes: ['opening_range', 'trend_following'],
        max_stocks: 3,
        timeframes: ['5m', '15m'],
        risk_per_trade: '1.0',
        sectors: ['IT', 'Banking', 'Pharma'],
        stock_universe: ['nifty50', 'fno'],
        smart_filter: true
      }
    },
    equity: {
      enabled: false,
      swing: {
        enabled: false,
        modes: ['momentum', 'breakout'],
        max_stocks: 5,
        sectors: ['IT', 'Banking', 'Auto'],
        scan_frequency: 'weekly',
        market_caps: ['largecap', 'midcap']
      }
    }
  });

  // Check if user is authenticated and load saved preferences when component mounts
  useEffect(() => {
    const checkAuth = async () => {
      // Check if token exists
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }
      
      setIsAuthenticated(true);
      
      // Load previously saved trading preferences
      try {
        const savedPreferences = localStorage.getItem('tradingPreferences');
        if (savedPreferences) {
          const parsedPreferences = JSON.parse(savedPreferences);
          
          // Update form data based on loaded preferences
          setFormData(prevData => {
            const updatedData = { ...prevData };
            
            // Update options trading settings
            if (parsedPreferences.options) {
              updatedData.options = {
                ...updatedData.options,
                ...parsedPreferences.options,
                enabled: parsedPreferences.options.enabled || false
              };
            }
            
            // Update intraday settings
            if (parsedPreferences.intraday) {
              updatedData.intraday.enabled = parsedPreferences.intraday.enabled || false;
              
              if (parsedPreferences.intraday.equity) {
                updatedData.intraday.equity = {
                  ...updatedData.intraday.equity,
                  ...parsedPreferences.intraday.equity,
                  enabled: parsedPreferences.intraday.equity.enabled || false
                };
              }
            }
            
            // Update equity settings
            if (parsedPreferences.equity) {
              updatedData.equity.enabled = parsedPreferences.equity.enabled || false;
              
              if (parsedPreferences.equity.swing) {
                updatedData.equity.swing = {
                  ...updatedData.equity.swing,
                  ...parsedPreferences.equity.swing,
                  enabled: parsedPreferences.equity.swing.enabled || false
                };
              }
            }
            
            return updatedData;
          });
        }
      } catch (error) {
        console.error('Error loading trading preferences:', error);
      }
    };
    
    checkAuth();
  }, [router]);

  // Handle options trading data change
  const handleOptionsChange = (optionsData: OptionsData) => {
    setFormData(prev => ({
      ...prev,
      options: optionsData
    }));
  };

  // Handle swing equity data change
  const handleSwingEquityChange = (swingData: SwingEquityData) => {
    setFormData(prev => ({
      ...prev,
      equity: {
        ...prev.equity,
        enabled: swingData.enabled || prev.equity.enabled,
        swing: swingData
      }
    }));
  };

  // Handle intraday equity data change
  const handleIntradayEquityChange = (intradayData: IntradayEquityData) => {
    setFormData(prev => ({
      ...prev,
      intraday: {
        ...prev.intraday,
        enabled: intradayData.enabled || prev.intraday.enabled,
        equity: intradayData
      }
    }));
  };

  // Submit form handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setIsSubmitting(true);
    
    try {
      // Create the preferences object with the new structure
      const tradingPreferences = {
        options: {
          enabled: formData.options.enabled,
          indexes: formData.options.indexes,
          modes: formData.options.modes,
          auto_execute: formData.options.auto_execute
        },
        intraday: {
          enabled: formData.intraday.enabled,
          equity: {
            enabled: formData.intraday.equity.enabled,
            modes: formData.intraday.equity.modes,
            max_stocks: formData.intraday.equity.max_stocks,
            timeframes: formData.intraday.equity.timeframes,
            risk_per_trade: formData.intraday.equity.risk_per_trade,
            sectors: formData.intraday.equity.sectors,
            stock_universe: formData.intraday.equity.stock_universe,
            smart_filter: formData.intraday.equity.smart_filter
          }
        },
        equity: {
          enabled: formData.equity.enabled,
          swing: {
            enabled: formData.equity.swing.enabled,
            modes: formData.equity.swing.modes,
            max_stocks: formData.equity.swing.max_stocks,
            sectors: formData.equity.swing.sectors,
            scan_frequency: formData.equity.swing.scan_frequency,
            market_caps: formData.equity.swing.market_caps
          }
        },
        // Backward compatibility for API
        auto_execute: formData.options.auto_execute,
        log_enabled: true
      };
      
      // Save both trading preferences and complete form data
      console.log('Saving trading preferences:', tradingPreferences);
      localStorage.setItem('tradingPreferences', JSON.stringify(tradingPreferences));
      localStorage.setItem('formData', JSON.stringify(formData));
      
      // Navigate to signals page
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
        <div className="max-w-7xl mx-auto px-4 py-8">
          <h1 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Configure Trading Mode
          </h1>

          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Column 1: Options Trading */}
              <OptionsTrading 
                data={formData.options} 
                onChange={handleOptionsChange} 
              />

              {/* Column 2: Equity Swing Trading */}
              <SwingEquityTrading 
                data={formData.equity.swing} 
                onChange={handleSwingEquityChange} 
              />

              {/* Column 3: Equity Intraday Trading */}
              <IntradayEquityTrading 
                data={formData.intraday.equity} 
                onChange={handleIntradayEquityChange} 
              />
            </div>

            {/* PDF Upload Row */}
            <div className="mt-6">
              <UploadPDF />
            </div>

            {/* Configuration Summary and Submit Button */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-6">
              <div className="md:col-span-3 bg-blue-50 p-4 rounded-lg border border-blue-100">
                <h3 className="text-sm font-medium text-blue-800 mb-2">Trading Configuration Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-blue-700">
                  {/* Options */}
                  <div className="space-y-1">
                    <div className="font-medium">Options Trading:</div>
                    <div className="flex items-center">
                      <span className={`inline-block w-2 h-2 rounded-full mr-2 ${formData.options.enabled ? 'bg-green-500' : 'bg-red-500'}`}></span>
                      <span>Status: {formData.options.enabled ? 'Enabled' : 'Disabled'}</span>
                    </div>
                    {formData.options.enabled && (
                      <>
                        <div className="flex items-center">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                          <span>Indexes: {formData.options.indexes.join(', ') || 'None selected'}</span>
                        </div>
                        <div className="flex items-center">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                          <span>Modes: {formData.options.modes.join(', ') || 'None selected'}</span>
                        </div>
                        <div className="flex items-center">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                          <span>Auto-execute: {formData.options.auto_execute ? 'Yes' : 'No'}</span>
                        </div>
                      </>
                    )}
                  </div>
                  
                  {/* Equity Swing */}
                  <div className="space-y-1">
                    <div className="font-medium">Swing Equity Trading:</div>
                    <div className="flex items-center">
                      <span className={`inline-block w-2 h-2 rounded-full mr-2 ${formData.equity.swing.enabled ? 'bg-green-500' : 'bg-red-500'}`}></span>
                      <span>
                        Status: {formData.equity.swing.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    {formData.equity.swing.enabled && (
                      <>
                        <div className="flex items-center">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                          <span>Strategies: {formData.equity.swing.modes.join(', ') || 'None selected'}</span>
                        </div>
                        <div className="flex items-center">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                          <span>Max stocks: {formData.equity.swing.max_stocks}</span>
                        </div>
                        <div className="flex items-center">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                          <span>Market Caps: {formData.equity.swing.market_caps.join(', ') || 'None selected'}</span>
                        </div>
                      </>
                    )}
                  </div>
                  
                  {/* Equity Intraday */}
                  <div className="space-y-1">
                    <div className="font-medium">Intraday Equity Trading:</div>
                    <div className="flex items-center">
                      <span className={`inline-block w-2 h-2 rounded-full mr-2 ${formData.intraday.equity.enabled ? 'bg-green-500' : 'bg-red-500'}`}></span>
                      <span>
                        Status: {formData.intraday.equity.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    {formData.intraday.equity.enabled && (
                      <>
                        <div className="flex items-center">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                          <span>Strategies: {formData.intraday.equity.modes.join(', ') || 'None selected'}</span>
                        </div>
                        <div className="flex items-center">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                          <span>Max stocks: {formData.intraday.equity.max_stocks}</span>
                        </div>
                        <div className="flex items-center">
                          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                          <span>Timeframes: {formData.intraday.equity.timeframes.join(', ') || 'None selected'}</span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="md:col-span-1">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={`w-full h-full py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${
                    isSubmitting ? 'opacity-75 cursor-not-allowed' : ''
                  }`}
                >
                  {isSubmitting ? 'Processing...' : 'Get Trading Signals'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </main>

      <Footer />
    </div>
  );
}