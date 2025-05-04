'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import MarketDataBar from '@/components/signals/MarketDataBar';
import ActivityLog from '@/components/signals/ActivityLog';
import { SignalResponse, LogEntry, MarketData, Signal } from '../../types/trading';
import { executeSignal, refreshSignals, fetchMarketData } from '../services/api';
import OptionsSignals from '@/components/signals/OptionsSignals';
import SwingEquitySignals from '@/components/signals/SwingEquitySignals';
import IntradayEquitySignals from '@/components/signals/IntradayEquitySignals';

// Mock data for equity signals since we're adding new components
const mockSwingSignals = [
  {
    id: 'swing-1',
    symbol: 'HDFCBANK',
    action: 'BUY' as const,
    entry_price: 1680.50,
    target_price: 1750.25,
    stop_loss: 1650.00,
    risk_reward: 2.3,
    potential_gain: 4.15,
    timeframe: 'Daily',
    confidence: 85,
    setup_type: 'Cup & Handle',
    sector: 'Banking',
    analysis: 'HDFC Bank is showing a strong cup and handle pattern on the daily timeframe. Volume profile supports the breakout and sector rotation indicators show renewed interest in banking stocks. The pattern targets 1750 with a favorable risk-reward ratio.',
    executed: false
  },
  {
    id: 'swing-2',
    symbol: 'INFY',
    action: 'BUY' as const,
    entry_price: 1450.75,
    target_price: 1520.00,
    stop_loss: 1420.50,
    risk_reward: 2.1,
    potential_gain: 4.8,
    timeframe: 'Daily',
    confidence: 78,
    setup_type: 'Breakout',
    sector: 'IT',
    analysis: 'Infosys is breaking out of a 3-month consolidation range with increasing volume. The IT sector is showing relative strength compared to the broader market. Key technical indicators including RSI and MACD support this bullish view.',
    executed: false
  }
];

const mockIntradaySignals = [
  {
    id: 'intraday-1',
    symbol: 'RELIANCE',
    action: 'BUY' as const,
    entry_price: 2580.25,
    target_price: 2605.50,
    stop_loss: 2565.00,
    risk_reward: 1.7,
    potential_gain: 0.98,
    timeframe: '15m',
    confidence: 82,
    strategy: 'Trend Following' as const,
    volume_surge: 1.5,
    key_level: 2575.00,
    trigger: 'Break above 15-min resistance',
    executed: false
  },
  {
    id: 'intraday-2',
    symbol: 'SBIN',
    action: 'SELL' as const,
    entry_price: 675.50,
    target_price: 665.25,
    stop_loss: 680.75,
    risk_reward: 1.9,
    potential_gain: 1.52,
    timeframe: '5m',
    confidence: 76,
    strategy: 'Mean Reversion' as const,
    volume_surge: 1.2,
    key_level: 678.00,
    trigger: 'Rejection at hourly resistance',
    executed: false
  },
  {
    id: 'intraday-3',
    symbol: 'TATAMOTORS',
    action: 'BUY' as const,
    entry_price: 875.25,
    target_price: 890.00,
    stop_loss: 868.00,
    risk_reward: 2.0,
    potential_gain: 1.69,
    timeframe: '5m',
    confidence: 88,
    strategy: 'Opening Range' as const,
    volume_surge: 2.3,
    key_level: 872.50,
    trigger: 'ORB 30-min breakout',
    executed: true
  }
];

export default function SignalsPage() {
  const router = useRouter();
  const [signals, setSignals] = useState<SignalResponse>({
    executed_signals: [],
    non_executed_signals: []
  });
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  
  // Load trading preferences to determine which modules to show
  const [tradingPreferences, setTradingPreferences] = useState({
    equity_swing: { enabled: true },
    equity_intraday: { enabled: true }
  });
  
  // Reference to store interval ID
  const intervalIdRef = useRef<NodeJS.Timeout | null>(null);

  // Use a single refresh interval for all data - 5 seconds (5000ms)
  const REFRESH_INTERVAL = 60000;

  // Create a modified logger that filters routine updates
  const maxLogs = 100; // Maximum number of logs to keep
  
  const logger = {
    // For trading signals only
    signal: (message: string) => setLogs(prevLogs => [{
      id: Date.now().toString(),
      type: 'info',
      message,
      timestamp: new Date().toISOString()
    }, ...prevLogs.slice(0, maxLogs - 1)]),
    
    // For successful trading operations
    success: (message: string) => setLogs(prevLogs => [{
      id: Date.now().toString(),
      type: 'success',
      message,
      timestamp: new Date().toISOString()
    }, ...prevLogs.slice(0, maxLogs - 1)]),
    
    // For warnings
    warning: (message: string) => setLogs(prevLogs => [{
      id: Date.now().toString(),
      type: 'warning',
      message,
      timestamp: new Date().toISOString()
    }, ...prevLogs.slice(0, maxLogs - 1)]),
    
    // For errors
    error: (message: string) => setLogs(prevLogs => [{
      id: Date.now().toString(),
      type: 'error',
      message,
      timestamp: new Date().toISOString()
    }, ...prevLogs.slice(0, maxLogs - 1)]),
    
    // Keep original info method for backward compatibility
    // but don't use it for routine updates
    info: (message: string) => console.log(message),
    
    clear: () => setLogs([])
  };

  const formatSignalDetails = (signal: any): string => {
    const direction = signal.action;
    let detailsText = '';
    
    if (signal.symbol && signal.strike && signal.optionType) {
      // Options signal
      const strikeInfo = `${signal.symbol} ${signal.strike} ${signal.optionType}`;
      const priceInfo = `Entry: ${signal.price.toFixed(2)}, Target: ${signal.target_price.toFixed(2)}, SL: ${signal.stop_loss.toFixed(2)}`;
      const rrrInfo = `RRR: ${signal.risk_reward_ratio.toFixed(2)}`;
      detailsText = `${direction} ${strikeInfo} - ${priceInfo} - ${rrrInfo}`;
    } else if (signal.strategy) {
      // Intraday signal
      detailsText = `${direction} ${signal.symbol} (${signal.strategy}) - Entry: ${signal.entry_price}, Target: ${signal.target_price}`;
    } else {
      // Swing signal
      detailsText = `${direction} ${signal.symbol} (${signal.setup_type}) - Entry: ${signal.entry_price}, Target: ${signal.target_price}`;
    }
    
    return detailsText;
  };

  // Centralized fetch function that updates both market data and signals
  const fetchAllData = useCallback(async () => {
    console.log(`[${new Date().toLocaleTimeString()}] Fetching all data...`);
    
    try {
      // First fetch market data
      const data = await fetchMarketData();
      setMarketData(data);
      
      // Then fetch signals (if not currently refreshing)
      if (!isRefreshing) {
        const response = await refreshSignals();
        
        // Use functional state update to avoid dependency on signals
        setSignals(prevSignals => {
          // Check for new signals compared to current state
          const currentSignalIds = prevSignals.non_executed_signals.map(s => s.id);
          const newSignals = response.non_executed_signals.filter(
            s => !currentSignalIds.includes(s.id)
          );
          
          // Log new signals
          if (newSignals.length > 0) {
            newSignals.forEach(signal => {
              logger.signal(`New Signal: ${formatSignalDetails(signal)}`);
            });
            logger.success(`Found ${newSignals.length} new trading signals`);
          }
          
          // Store in localStorage
          localStorage.setItem('tradingSignals', JSON.stringify(response));
          
          return response;
        });
      }
      
      // Update the last updated timestamp
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching data:', error);
      logger.error('Failed to update data');
    }
  }, [isRefreshing]);

  const loadStoredSignals = useCallback(async () => {
    const storedSignals = localStorage.getItem('tradingSignals');
    if (storedSignals) {
      try {
        const parsedSignals = JSON.parse(storedSignals);
        setSignals(parsedSignals);
      } catch (error) {
        console.error('Error parsing signals:', error);
        logger.error('Failed to load stored signals');
      }
    } else {
      // If no stored signals, fetch signals but don't log them yet
      try {
        const response = await refreshSignals();
        setSignals(response);
        localStorage.setItem('tradingSignals', JSON.stringify(response));
      } catch (error) {
        console.error('Error loading default signals:', error);
        logger.error('Failed to load default signals');
      }
    }
    
    // Load trading preferences
    const storedPreferences = localStorage.getItem('tradingPreferences');
    if (storedPreferences) {
      try {
        const parsedPreferences = JSON.parse(storedPreferences);
        setTradingPreferences(parsedPreferences);
      } catch (error) {
        console.error('Error parsing trading preferences:', error);
      }
    }
  }, []);

  // Initial load effect
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      setIsAuthenticated(true);

      // Load initial data
      Promise.all([
        loadStoredSignals(),
        fetchMarketData().then(data => setMarketData(data))
      ]).then(() => {
        setLoading(false);
      }).catch(error => {
        console.error('Error loading initial data:', error);
        logger.error('Failed to initialize dashboard');
        setLoading(false);
      });
    };

    const timer = setTimeout(() => {
      checkAuth();
    }, 0);

    return () => clearTimeout(timer);
  }, [router, loadStoredSignals]);

  // Set up a single data fetch interval with improved cleanup
  useEffect(() => {
    if (!isAuthenticated) return;
    
    console.log(`Setting up refresh interval (${REFRESH_INTERVAL}ms)`);
    
    // Initial fetch
    fetchAllData();
    
    // Clear any existing interval first
    if (intervalIdRef.current) {
      clearInterval(intervalIdRef.current);
      intervalIdRef.current = null;
    }
    
    // Set up interval and store the reference
    intervalIdRef.current = setInterval(() => {
      console.log(`[${new Date().toLocaleTimeString()}] Interval triggered`);
      fetchAllData();
    }, REFRESH_INTERVAL);
    
    // Clean up interval on unmount or when dependencies change
    return () => {
      console.log('Clearing refresh interval');
      if (intervalIdRef.current) {
        clearInterval(intervalIdRef.current);
        intervalIdRef.current = null;
      }
    };
  }, [isAuthenticated, fetchAllData]);

  const handleManualExecution = async (signalId: string) => {
    try {
      // Find the signal to be executed (options, swing, or intraday)
      const signalToExecute = signals.non_executed_signals.find(s => s.id === signalId) ||
                             mockSwingSignals.find(s => s.id === signalId) ||
                             mockIntradaySignals.find(s => s.id === signalId);
                             
      if (!signalToExecute) {
        logger.error(`Signal ${signalId} not found`);
        return;
      }
      
      // Log with meaningful details
      logger.signal(`Executing Trade: ${formatSignalDetails(signalToExecute)}`);
      
      // If it's an options signal, use the regular flow
      if (signalId.indexOf('swing') === -1 && signalId.indexOf('intraday') === -1) {
        const response = await executeSignal(signalId);

        setSignals(prevSignals => {
          const signalToMove = prevSignals.non_executed_signals.find(s => s.id === signalId);
          if (!signalToMove) return prevSignals;

          const updatedSignal = {
            ...signalToMove,
            executed: true,
            executed_at: new Date().toISOString(),
            order_id: response.order_id
          };

          const newSignals = {
            executed_signals: [...prevSignals.executed_signals, updatedSignal],
            non_executed_signals: prevSignals.non_executed_signals.filter(s => s.id !== signalId)
          };

          localStorage.setItem('tradingSignals', JSON.stringify(newSignals));
          
          // Log success with meaningful details
          logger.success(`Order Executed: ${formatSignalDetails(signalToMove)} (Order ID: ${response.order_id})`);
          
          return newSignals;
        });
      }
      // For equity signals (both swing and intraday), handle mock execution
      else {
        // Mock execution response
        const mockResponse = {
          order_id: `ORD-${Date.now().toString().substring(7)}`,
          status: 'success'
        };
        
        // Update mock data (in a real app, we'd update the API/backend)
        if (signalId.indexOf('swing') >= 0) {
          mockSwingSignals.forEach(signal => {
            if (signal.id === signalId) {
              signal.executed = true;
            }
          });
        } else {
          mockIntradaySignals.forEach(signal => {
            if (signal.id === signalId) {
              signal.executed = true;
            }
          });
        }
        
        // Log success
        logger.success(`Order Executed: ${formatSignalDetails(signalToExecute)} (Order ID: ${mockResponse.order_id})`);
      }
    } catch (error) {
      console.error('Error executing signal:', error);
      logger.error(`Failed to execute signal ${signalId}`);
    }
  };

  const handleManualRefresh = async () => {
    setIsRefreshing(true);

    try {
      await fetchAllData();
      logger.success('Data refreshed manually');
    } catch (error) {
      console.error('Error during manual refresh:', error);
      logger.error('Manual refresh failed');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleBackToSelection = () => {
    router.push('/selection');
  };

  // Filter options signals
  const getOptionsSignals = () => {
    // Filter signals that appear to be options (have strike and optionType)
    const optionSignals = signals.non_executed_signals.filter(
      signal => signal.instrumentType === 'Option' || 
               (signal.strike && signal.optionType)
    );
    
    const executedOptionSignals = signals.executed_signals.filter(
      signal => signal.instrumentType === 'Option' || 
               (signal.strike && signal.optionType)
    );
    
    return {
      availableSignals: optionSignals,
      executedSignals: executedOptionSignals
    };
  };

  if (!isAuthenticated || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-green-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Header showActions={true} />
      <main className="flex-grow bg-gradient-to-br from-white to-green-50 py-6">
        <div className="max-w-7xl mx-auto px-4">
          {/* Top bar with market data and controls */}
          <div className="mb-6">
            <MarketDataBar 
              marketData={marketData} 
              refreshInterval={60000}  
            />
            
            <div className="flex justify-between items-center mt-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Trading Signals</h1>
                <p className="text-xs text-gray-500">
                  Last updated: {lastUpdated.toLocaleTimeString()} • Auto-refresh: {REFRESH_INTERVAL/1000}s
                </p>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={handleManualRefresh}
                  disabled={isRefreshing}
                  className={`px-4 py-2 text-sm rounded-md bg-white border border-green-300 shadow-sm hover:bg-green-50 ${
                    isRefreshing ? 'opacity-75 cursor-not-allowed' : ''
                  }`}
                >
                  {isRefreshing ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Refreshing...
                    </span>
                  ) : 'Manual Refresh'}
                </button>
                <button
                  onClick={handleBackToSelection}
                  className="px-4 py-2 text-sm bg-green-100 text-green-800 rounded-md hover:bg-green-200"
                >
                  ← Change Selection
                </button>
              </div>
            </div>
          </div>

          {/* Trading Modules - Grid Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Options Trading Module */}
            <div className="lg:col-span-1">
              <OptionsSignals
                availableSignals={getOptionsSignals().availableSignals}
                executedSignals={getOptionsSignals().executedSignals}
                onExecute={handleManualExecution}
                isLoading={isRefreshing}
              />
            </div>
            
            {/* Equity Trading Modules */}
            <div className="lg:col-span-1 space-y-6">
              {/* Swing Equity Trading Module */}
              {tradingPreferences.equity_swing?.enabled && (
                <SwingEquitySignals
                  signals={mockSwingSignals}
                  onExecute={handleManualExecution}
                  isLoading={isRefreshing}
                />
              )}
              
              {/* Intraday Equity Trading Module */}
              {tradingPreferences.equity_intraday?.enabled && (
                <IntradayEquitySignals
                  signals={mockIntradaySignals}
                  onExecute={handleManualExecution}
                  isLoading={isRefreshing}
                />
              )}
            </div>
          </div>

          {/* Activity Log at the bottom */}
          <ActivityLog logs={logs} onClear={logger.clear} />
        </div>
      </main>
      <Footer />
    </div>
  );
}