'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import MarketDataBar from '@/components/signals/MarketDataBar';
import SignalsList from '@/components/signals/SignalsList';
import ActivityLog from '@/components/signals/ActivityLog';
import { SignalResponse, LogEntry, MarketData } from '../../types/trading';
import { executeSignal, refreshSignals, fetchMarketData } from '../services/api';
import { createLogger } from '../utils/logger';

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

  const loadMarketData = useCallback(async () => {
    try {
      const data = await fetchMarketData();
      setMarketData(data);
      // Don't log this routine update
    } catch (error) {
      console.error('Error fetching market data:', error);
      logger.error('Failed to update market data');
    }
  }, []);

  const formatSignalDetails = (signal: any): string => {
    const direction = signal.action;
    const strikeInfo = `${signal.symbol} ${signal.strike} ${signal.optionType}`;
    const priceInfo = `Entry: ${signal.price.toFixed(2)}, Target: ${signal.target_price.toFixed(2)}, SL: ${signal.stop_loss.toFixed(2)}`;
    const rrrInfo = `RRR: ${signal.risk_reward_ratio.toFixed(2)}`;
    
    return `${direction} ${strikeInfo} - ${priceInfo} - ${rrrInfo}`;
  };

  const loadStoredSignals = useCallback(async () => {
    const storedSignals = localStorage.getItem('tradingSignals');
    if (storedSignals) {
      try {
        const parsedSignals = JSON.parse(storedSignals);
        
        // Check for new signals compared to current state
        const currentSignalIds = signals.non_executed_signals.map(s => s.id);
        const newSignals = parsedSignals.non_executed_signals.filter(
          (s: any) => !currentSignalIds.includes(s.id)
        );
        
        // Log new signals
        if (newSignals.length > 0) {
          newSignals.forEach((signal: any) => {
            logger.signal(`New Signal: ${formatSignalDetails(signal)}`);
          });
        }
        
        setSignals(parsedSignals);
      } catch (error) {
        console.error('Error parsing signals:', error);
        logger.error('Failed to load stored signals');
      }
    } else {
      try {
        const response = await refreshSignals();
        
        // Log any signals that were loaded
        if (response.non_executed_signals.length > 0) {
          response.non_executed_signals.forEach(signal => {
            logger.signal(`New Signal: ${formatSignalDetails(signal)}`);
          });
        }
        
        setSignals(response);
        localStorage.setItem('tradingSignals', JSON.stringify(response));
      } catch (error) {
        console.error('Error loading default signals:', error);
        logger.error('Failed to load default signals');
      }
    }
  }, [signals.non_executed_signals]);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      setIsAuthenticated(true);

      Promise.all([
        loadStoredSignals(),
        loadMarketData()
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
  }, [router, loadStoredSignals, loadMarketData]);

  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(() => {
      loadMarketData();
    }, 60000);

    return () => clearInterval(interval);
  }, [isAuthenticated, loadMarketData]);

  const handleManualExecution = async (signalId: string) => {
    try {
      // Find the signal to be executed
      const signalToExecute = signals.non_executed_signals.find(s => s.id === signalId);
      if (!signalToExecute) {
        logger.error(`Signal ${signalId} not found`);
        return;
      }
      
      // Log with meaningful details
      logger.signal(`Executing Trade: ${formatSignalDetails(signalToExecute)}`);
      
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
    } catch (error) {
      console.error('Error executing signal:', error);
      logger.error(`Failed to execute signal ${signalId}`);
    }
  };

  const handleRefreshSignals = async () => {
    setIsRefreshing(true);

    try {
      const prevSignalIds = signals.non_executed_signals.map(s => s.id);
      const response = await refreshSignals();
      
      // Check for new signals
      const newSignals = response.non_executed_signals.filter(
        s => !prevSignalIds.includes(s.id)
      );
      
      // Log each new signal
      if (newSignals.length > 0) {
        newSignals.forEach(signal => {
          logger.signal(`New Signal: ${formatSignalDetails(signal)}`);
        });
        logger.success(`Found ${newSignals.length} new trading signals`);
      } else {
      }
      
      setSignals(response);
      localStorage.setItem('tradingSignals', JSON.stringify(response));
    } catch (error) {
      console.error('Error refreshing signals:', error);
      logger.error('Failed to refresh signals');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleBackToSelection = () => {
    router.push('/selection');
  };

  // Future function for closing positions
  const handleClosePosition = async (signalId: string) => {
    try {
      // Find the signal being closed
      const signalToClose = signals.executed_signals.find(s => s.id === signalId);
      if (!signalToClose) {
        logger.error(`Signal ${signalId} not found`);
        return;
      }
      
      // Log exit intent
      logger.signal(`Closing Position: ${formatSignalDetails(signalToClose)}`);
      
      // API call would go here
      // const response = await closePosition(signalId);
      
      // Update state, etc.
      
      // Log success
      logger.success(`Position Closed: ${formatSignalDetails(signalToClose)} (PnL: +₹1,250)`);
    } catch (error) {
      console.error('Error closing position:', error);
      logger.error(`Failed to close position ${signalId}`);
    }
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
        <MarketDataBar marketData={marketData} refreshInterval={60000} />
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Trading Signals</h1>
            <div className="flex space-x-3">
              <button
                onClick={handleRefreshSignals}
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
                ) : 'Refresh Signals'}
              </button>
              <button
                onClick={handleBackToSelection}
                className="px-4 py-2 text-sm bg-green-100 text-green-800 rounded-md hover:bg-green-200"
              >
                ← Change Selection
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <SignalsList
              title="✅ Ongoing Trades"
              signals={signals.executed_signals}
              isExecuted={true}
              emptyMessage={{
                primary: "No active trades at the moment.",
                secondary: "Execute a signal to see it here."
              }}
            />

            <SignalsList
              title="💡 Available Signals"
              signals={signals.non_executed_signals}
              isExecuted={false}
              onExecute={handleManualExecution}
              emptyMessage={{
                primary: "No available signals at the moment.",
                secondary: "Try refreshing or changing your selection criteria."
              }}
            />
          </div>

          <ActivityLog logs={logs} onClear={logger.clear} />
        </div>
      </main>
      <Footer />
    </div>
  );
}