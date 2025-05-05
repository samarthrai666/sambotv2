// frontend/app/signals/page.tsx
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
import { convertToSwingEquityFormat, convertToIntradayFormat, extractEquitySignals } from '../utils/signalAdapters';

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
  
  // Store processed equity signals
  const [equitySignals, setEquitySignals] = useState<any[]>([]);
  
  // Load trading preferences to determine which modules to show
  const [tradingPreferences, setTradingPreferences] = useState({
    equity_swing: { enabled: true },
    equity_intraday: { enabled: true }
  });
  
  // Reference to store interval ID
  const intervalIdRef = useRef<NodeJS.Timeout | null>(null);

  // Use a single refresh interval for all data - 60 seconds (60000ms)
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
      const priceInfo = `Entry: ${(signal.price || signal.entry_price).toFixed(2)}, Target: ${(signal.target_price || signal.target).toFixed(2)}, SL: ${signal.stop_loss.toFixed(2)}`;
      const rrrInfo = `RRR: ${(signal.risk_reward_ratio || signal.risk_reward || signal.rrr || 1).toFixed(2)}`;
      detailsText = `${direction} ${strikeInfo} - ${priceInfo} - ${rrrInfo}`;
    } else if (signal.strategy) {
      // Intraday signal
      detailsText = `${direction} ${signal.symbol} (${signal.strategy}) - Entry: ${(signal.entry_price || signal.price || signal.entry).toFixed(2)}, Target: ${(signal.target_price || signal.target).toFixed(2)}`;
    } else {
      // Swing signal
      detailsText = `${direction} ${signal.symbol} (${signal.setup_type || 'Swing'}) - Entry: ${(signal.entry_price || signal.price || signal.entry).toFixed(2)}, Target: ${(signal.target_price || signal.target).toFixed(2)}`;
    }
    
    return detailsText;
  };

  // Process signals when non_executed_signals changes
  useEffect(() => {
    if (signals.non_executed_signals && signals.non_executed_signals.length > 0) {
      const equitySignalsFromAPI = extractEquitySignals(signals.non_executed_signals);
      
      if (equitySignalsFromAPI.length > 0) {
        console.log('Found equity signals:', equitySignalsFromAPI);
        setEquitySignals(convertToSwingEquityFormat(equitySignalsFromAPI));
      } else {
        console.log('No equity signals found in API response');
        // Clear equity signals when no signals are found
        setEquitySignals([]);
      }
    } else {
      // Clear equity signals when no signals are returned
      setEquitySignals([]);
    }
  }, [signals.non_executed_signals]);

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
      // Find the signal to be executed (options or equity)
      const signalToExecute = signals.non_executed_signals.find(s => s.id === signalId) ||
                              equitySignals.find(s => s.id === signalId);
                             
      if (!signalToExecute) {
        logger.error(`Signal ${signalId} not found`);
        return;
      }
      
      // Log with meaningful details
      logger.signal(`Executing Trade: ${formatSignalDetails(signalToExecute)}`);
      
      // If it's an options signal, use the regular flow
      if (signalId.indexOf('equity') === -1) {
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
      // For equity signals, handle execution
      else {
        // Call execute signal API
        const response = await executeSignal(signalId);
        
        // Update equity signals state
        setEquitySignals(prevSignals => {
          return prevSignals.map(signal => 
            signal.id === signalId 
              ? { ...signal, executed: true, order_id: response.order_id } 
              : signal
          );
        });
        
        // Log success
        logger.success(`Order Executed: ${formatSignalDetails(signalToExecute)} (Order ID: ${response.order_id})`);
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

  // Get intraday signals
  const getIntradaySignals = () => {
    const intradaySignals = signals.non_executed_signals.filter(
      signal => signal.timeframe === '5m' || signal.timeframe === '15m' || signal.timeframe === '1m'
    );
    
    return convertToIntradayFormat(intradaySignals);
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
              {tradingPreferences.options?.enabled && (
                <OptionsSignals
                  availableSignals={getOptionsSignals().availableSignals}
                  executedSignals={getOptionsSignals().executedSignals}
                  onExecute={handleManualExecution}
                  isLoading={isRefreshing}
                />
              )}
            </div>
            
            {/* Equity Trading Modules */}
            <div className="lg:col-span-1 space-y-6">
              {/* Swing Equity Trading Module */}
              {tradingPreferences.equity?.swing?.enabled && (
                <SwingEquitySignals
                  signals={equitySignals}
                  onExecute={handleManualExecution}
                  isLoading={isRefreshing}
                />
              )}
              
              {/* Intraday Equity Trading Module */}
              {tradingPreferences.intraday?.equity?.enabled && (
                <IntradayEquitySignals
                  signals={getIntradaySignals()}
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