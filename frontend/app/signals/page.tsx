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

  const logger = createLogger(setLogs);

  const loadMarketData = useCallback(async () => {
    try {
      const data = await fetchMarketData();
      setMarketData(data);
      logger.info('Market data updated');
    } catch (error) {
      console.error('Error fetching market data:', error);
      logger.error('Failed to update market data');
    }
  }, [logger]);

  const loadStoredSignals = useCallback(async () => {
    const storedSignals = localStorage.getItem('tradingSignals');
    if (storedSignals) {
      try {
        setSignals(JSON.parse(storedSignals));
      } catch (error) {
        console.error('Error parsing signals:', error);
        logger.error('Failed to load stored signals');
      }
    } else {
      try {
        const response = await refreshSignals();
        setSignals(response);
        localStorage.setItem('tradingSignals', JSON.stringify(response));
        logger.info('Loaded default signals');
      } catch (error) {
        console.error('Error loading default signals:', error);
        logger.error('Failed to load default signals');
      }
    }
  }, [logger]);

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
        logger.info('Dashboard initialized successfully');
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
  }, [router, loadStoredSignals, loadMarketData, logger]);

  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(() => {
      loadMarketData();
    }, 60000);

    return () => clearInterval(interval);
  }, [isAuthenticated, loadMarketData]);

  const handleManualExecution = async (signalId: string) => {
    try {
      logger.info(`Executing signal ${signalId}...`);
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
        logger.success(`Signal ${signalId} executed successfully (Order ID: ${response.order_id})`);
        return newSignals;
      });
    } catch (error) {
      console.error('Error executing signal:', error);
      logger.error(`Failed to execute signal ${signalId}`);
    }
  };

  const handleRefreshSignals = async () => {
    setIsRefreshing(true);
    logger.info('Refreshing signals...');

    try {
      const response = await refreshSignals();
      setSignals(response);
      localStorage.setItem('tradingSignals', JSON.stringify(response));
      logger.success('Signals refreshed successfully');
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
          <MarketDataBar marketData={marketData} />
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
